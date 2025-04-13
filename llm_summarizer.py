from typing import Dict, Any
from rich.console import Console
from config import LLMConfig
from llama_cpp import Llama
import os

console = Console()

def create_summarization_prompt(pr_data: Dict[str, Any]) -> str:
    return f"""Please provide a detailed summary of the following GitHub Pull Request:

Title: {pr_data.get('title', 'N/A')}
Repository: {pr_data.get('repository_url', 'N/A')}
Created At: {pr_data.get('created_at', 'N/A')}
Description: {pr_data.get('body', 'N/A')}

Please include:
1. Key changes and features
2. Technical details
3. Impact and significance
4. Any notable discussions or decisions

Format the summary in a clear, professional manner."""

def summarize_pr(pr_data: Dict[str, Any], config: LLMConfig, model_path: str) -> str:
    try:
        # Initialize the Llama model
        llm = Llama(
            model_path=model_path,
            n_ctx=2048,  # Context window size
            n_threads=4  # Number of CPU threads to use
        )
        
        # Create the prompt
        prompt = create_summarization_prompt(pr_data)
        
        # Generate the summary
        output = llm(
            prompt,
            max_tokens=config.max_tokens,
            temperature=config.temperature,
            stop=["</s>", "###"]  # Stop tokens
        )
        
        return output['choices'][0]['text'].strip()
        
    except Exception as e:
        console.print(f"[red]Error generating summary: {str(e)}")
        return "Error generating summary" 