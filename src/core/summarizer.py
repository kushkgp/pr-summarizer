from typing import Dict, Any
from llama_cpp import Llama
import logging
from src.config.settings import LLMConfig

logger = logging.getLogger(__name__)

class LLMSummarizer:
    """Handles PR summarization using LLM."""
    
    def __init__(self, config: LLMConfig):
        """Initialize summarizer with LLM configuration."""
        self.config = config
        self.model = None
        
    def _initialize_model(self) -> None:
        """Initialize the LLM model if not already initialized."""
        if self.model is None:
            try:
                self.model = Llama(
                    model_path=self.config.model_path,
                    n_ctx=self.config.max_tokens,
                    n_threads=4
                )
            except Exception as e:
                logger.error(f"Failed to initialize LLM model: {str(e)}")
                raise

    def summarize(self, pr_data: Dict[str, Any]) -> str:
        """Generate a summary for a pull request."""
        self._initialize_model()
        
        prompt = self._create_prompt(pr_data)
        
        try:
            response = self.model(
                prompt,
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature,
                top_p=self.config.top_p,
                repeat_penalty=self.config.repeat_penalty,
                stop=["</summary>"]
            )
            return response["choices"][0]["text"].strip()
        except Exception as e:
            logger.error(f"Failed to generate summary: {str(e)}")
            return "Failed to generate summary."

    def _create_prompt(self, pr_data: Dict[str, Any]) -> str:
        """Create a prompt for the LLM."""
        return f"""Please provide a concise summary of the following pull request:

Title: {pr_data['title']}
Description: {pr_data['body']}

Focus on:
1. The main changes or features
2. Any significant technical decisions
3. Impact on the codebase

Summary:""" 