from typing import List, Dict, Any
import logging
from contextlib import contextmanager
import sys
import os
import platform

from src.config.settings import LLMConfig

logger = logging.getLogger(__name__)

@contextmanager
def suppress_stdout():
    """Temporarily suppress stdout."""
    with open(os.devnull, 'w') as devnull:
        old_stdout = sys.stdout
        sys.stdout = devnull
        try:
            yield
        finally:
            sys.stdout = old_stdout

class LLMSummarizer:
    """Summarizes PRs using a local LLM."""
    
    def __init__(self, config: LLMConfig):
        """Initialize the summarizer with LLM configuration."""
        self.config = config
        self.model = None
        self._load_model()
        logger.debug("LLMSummarizer initialized")

    def _load_model(self) -> None:
        """Load the LLM model with Metal acceleration if available."""
        try:
            with suppress_stdout():
                from llama_cpp import Llama
                
                # Check if we're on Apple Silicon and Metal is requested
                use_metal = (
                    self.config.use_metal and 
                    platform.system() == "Darwin" and 
                    platform.machine() == "arm64"
                )
                
                if use_metal:
                    logger.info("Using Metal acceleration for Apple Silicon")
                    self.model = Llama(
                        model_path=self.config.model_path,
                        n_ctx=self.config.context_window,
                        n_threads=self.config.n_threads,
                        n_gpu_layers=self.config.n_gpu_layers,
                        use_mlock=True,  # Lock model in memory
                        use_mmap=True,   # Use memory mapping
                        offload_kqv=True # Offload key/value matrices to GPU
                    )
                else:
                    logger.info("Using CPU inference")
                    self.model = Llama(
                        model_path=self.config.model_path,
                        n_ctx=self.config.context_window,
                        n_threads=self.config.n_threads
                    )
                
            logger.debug("LLM model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load LLM model: {str(e)}", exc_info=True)
            raise

    def _format_pr_prompt(self, pr_data: Dict[str, Any]) -> str:
        """Format PR data into a prompt for the LLM."""
        return f"""Please provide a concise summary of this pull request:

Title: {pr_data.get('title', 'N/A')}
Description: {pr_data.get('body', 'N/A')}
Created At: {pr_data.get('created_at', 'N/A')}
Status: {pr_data.get('state', 'N/A')}

Focus on:
1. The main purpose of the changes
2. Key technical details
3. Impact on the codebase

Summary:"""

    def _format_all_prs_prompt(self, prs: List[Dict[str, Any]]) -> str:
        """Format all PRs into a single prompt for the LLM."""
        prompt = "Please provide concise summaries for each of these pull requests:\n\n"
        
        for i, pr in enumerate(prs, 1):
            prompt += f"PR #{i}:\n"
            prompt += f"Title: {pr.get('title', 'N/A')}\n"
            prompt += f"Description: {pr.get('body', 'N/A')}\n"
            prompt += f"Created At: {pr.get('created_at', 'N/A')}\n"
            prompt += f"Status: {pr.get('state', 'N/A')}\n\n"
        
        prompt += """For each PR, focus on:
1. The main purpose of the changes
2. Key technical details
3. Impact on the codebase

Provide the summaries in order, separated by "---" between each PR summary."""
        
        return prompt

    def summarize(self, pr_data: Dict[str, Any]) -> str:
        """Generate a summary for a single PR."""
        if not self.model:
            raise RuntimeError("LLM model not loaded")
        
        prompt = self._format_pr_prompt(pr_data)
        
        try:
            with suppress_stdout():
                response = self.model(
                    prompt,
                    max_tokens=self.config.max_tokens,
                    temperature=self.config.temperature,
                    stop=["---"]
                )
            return response['choices'][0]['text'].strip()
        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}", exc_info=True)
            return "Error generating summary"

    def summarize_all(self, prs: List[Dict[str, Any]]) -> List[str]:
        """Generate summaries for all PRs in a single LLM call."""
        if not self.model:
            raise RuntimeError("LLM model not loaded")
        
        prompt = self._format_all_prs_prompt(prs)
        
        try:
            with suppress_stdout():
                response = self.model(
                    prompt,
                    max_tokens=self.config.max_tokens * len(prs),  # Allocate more tokens for multiple PRs
                    temperature=self.config.temperature,
                    stop=["---"]
                )
            # Split the response into individual summaries
            summaries = response['choices'][0]['text'].strip().split("---")
            # Clean up each summary and ensure we have the right number
            summaries = [s.strip() for s in summaries if s.strip()]
            if len(summaries) != len(prs):
                logger.warning(f"Expected {len(prs)} summaries but got {len(summaries)}")
                # Pad or truncate as needed
                summaries = summaries[:len(prs)]
                while len(summaries) < len(prs):
                    summaries.append("Summary not available")
            return summaries
        except Exception as e:
            logger.error(f"Error generating summaries: {str(e)}", exc_info=True)
            return ["Error generating summary"] * len(prs) 