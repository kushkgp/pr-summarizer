import argparse
from typing import List, Dict, Any
from rich.console import Console
from rich.markdown import Markdown
from datetime import datetime
import json
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from rich import print as rprint
from rich.logging import RichHandler
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeRemainingColumn
from dotenv import load_dotenv
import os
import logging
import time

from config import AppConfig, LLMConfig
from github_client import GitHubClient
from llm_summarizer import summarize_pr

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichHandler(rich_tracebacks=True)]
)
logger = logging.getLogger("pr_summarizer")

console = Console()
MODEL_PATH = "models/mistral-7b-instruct-v0.2.Q4_K_M.gguf"

def get_repo_input() -> str:
    """Get repository name from user input."""
    return Prompt.ask("Enter GitHub repository (owner/repo)")

def display_pr_summary(pr_data: dict, summary: str):
    """Display PR information and summary in a formatted way."""
    # Create a table for PR information
    table = Table(title=f"PR #{pr_data.get('number', 'N/A')} Information", show_header=True, header_style="bold magenta")
    table.add_column("Field", style="cyan")
    table.add_column("Value", style="green")
    
    table.add_row("Title", pr_data.get('title', 'N/A'))
    table.add_row("Repository", pr_data.get('repository_url', 'N/A'))
    table.add_row("Created At", pr_data.get('created_at', 'N/A'))
    table.add_row("Status", pr_data.get('state', 'N/A'))
    
    console.print(table)
    console.print("\n")
    
    # Display the summary in a panel
    console.print(Panel(summary, title="PR Summary", border_style="blue"))
    console.print("\n" + "="*80 + "\n")

def main():
    logger.info("Starting PR Summarizer")
    
    # Load environment variables
    load_dotenv()
    logger.info("Environment variables loaded")
    
    # Get configuration
    config = AppConfig()
    logger.info("Configuration loaded")
    
    # Get repository input
    repo = get_repo_input()
    logger.info(f"Selected repository: {repo}")
    
    try:
        # Initialize GitHub client
        logger.info("Initializing GitHub client")
        github_client = GitHubClient(config.github_token)
        
        # Get recent PRs
        logger.info(f"Fetching recent PRs for {repo}")
        prs = github_client.get_recent_prs(repo)
        
        if not prs:
            logger.error("No PRs found or failed to fetch PRs")
            return
        
        # Check if model exists
        if not os.path.exists(MODEL_PATH):
            logger.error(f"Model not found at {MODEL_PATH}. Please run download_model.py first.")
            return
        
        # Process each PR
        logger.info(f"Processing {len(prs)} PRs")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            TimeRemainingColumn(),
            console=console
        ) as progress:
            task = progress.add_task("[cyan]Summarizing PRs...", total=len(prs))
            
            for pr_data in prs:
                logger.info(f"Processing PR #{pr_data['number']}: {pr_data['title']}")
                
                # Generate summary
                logger.info("Initializing LLM for summary generation")
                start_time = time.time()
                summary = summarize_pr(pr_data, config.llm_config, MODEL_PATH)
                duration = time.time() - start_time
                logger.info(f"LLM summary generated in {duration:.2f} seconds")
                
                # Display results
                display_pr_summary(pr_data, summary)
                progress.update(task, advance=1)
        
        logger.info("All PRs processed successfully")
        
    except Exception as e:
        logger.error(f"Error: {str(e)}", exc_info=True)

if __name__ == "__main__":
    main() 