import logging
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeRemainingColumn
from rich.markdown import Markdown
from rich.syntax import Syntax
from rich.text import Text
from datetime import datetime
from dotenv import load_dotenv
import os
import time
from typing import List, Dict, Any

from pr_summarizer.config.config import AppConfig
from pr_summarizer.core.github_client import GitHubClient
from pr_summarizer.models.summarizer import PRSummarizer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("pr_summarizer")

console = Console()
MODEL_PATH = "models/mistral-7b-instruct-v0.2.Q4_K_M.gguf"

def get_repo_input() -> str:
    """Get repository name from user input."""
    return Prompt.ask("Enter GitHub repository (owner/repo)")

def format_date(date_str: str) -> str:
    """Format date string to a more readable format."""
    try:
        date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return date.strftime("%B %d, %Y at %I:%M %p")
    except:
        return date_str

def display_pr_summary(pr_data: dict, summary: str):
    """Display PR information and summary in a formatted way."""
    # Create a table for PR information
    table = Table(
        title=f"PR #{pr_data.get('number', 'N/A')} Information",
        show_header=True,
        header_style="bold magenta",
        border_style="blue",
        title_style="bold cyan"
    )
    table.add_column("Field", style="cyan", width=20)
    table.add_column("Value", style="green")
    
    # Add PR information
    table.add_row("Title", pr_data.get('title', 'N/A'))
    table.add_row("Author", pr_data.get('user', {}).get('login', 'N/A'))
    table.add_row("Repository", pr_data.get('repository_url', 'N/A').split('/')[-1])
    table.add_row("Created", format_date(pr_data.get('created_at', 'N/A')))
    table.add_row("Updated", format_date(pr_data.get('updated_at', 'N/A')))
    table.add_row("Status", pr_data.get('state', 'N/A').upper())
    table.add_row("Merged", "Yes" if pr_data.get('merged_at') else "No")
    
    # Add PR stats
    stats = f"Commits: {pr_data.get('commits', 0)} | " \
            f"Additions: {pr_data.get('additions', 0)} | " \
            f"Deletions: {pr_data.get('deletions', 0)} | " \
            f"Changed Files: {pr_data.get('changed_files', 0)}"
    table.add_row("Stats", stats)
    
    console.print("\n")
    console.print(table)
    console.print("\n")
    
    # Display PR description if available
    if pr_data.get('body'):
        console.print(Panel(
            Markdown(pr_data['body']),
            title="PR Description",
            border_style="yellow"
        ))
        console.print("\n")
    
    # Display the summary in a panel with better formatting
    console.print(Panel(
        Markdown(summary),
        title="PR Summary",
        border_style="blue",
        title_style="bold cyan"
    ))
    
    # Add a separator
    console.print("\n" + "="*100 + "\n")

def display_all_summaries(summaries: List[Dict[str, Any]]):
    """Display all PR summaries in a single view."""
    console.print("\n" + "="*100)
    console.print(Panel(
        "All PR Summaries",
        style="bold cyan",
        border_style="blue"
    ))
    console.print("="*100 + "\n")
    
    for summary_data in summaries:
        pr_data = summary_data['pr_data']
        summary = summary_data['summary']
        
        # Create a compact table for each PR
        table = Table(
            show_header=False,
            border_style="blue",
            box=None
        )
        table.add_column("Field", style="cyan", width=15)
        table.add_column("Value", style="green")
        
        table.add_row("PR #", str(pr_data.get('number', 'N/A')))
        table.add_row("Title", pr_data.get('title', 'N/A'))
        table.add_row("Author", pr_data.get('user', {}).get('login', 'N/A'))
        table.add_row("Status", pr_data.get('state', 'N/A').upper())
        
        console.print(table)
        console.print(Panel(
            Markdown(summary),
            border_style="blue"
        ))
        console.print("\n" + "-"*100 + "\n")

def main():
    logger.info("Starting PR Summarizer")
    
    # Load environment variables
    load_dotenv()
    logger.info("Environment variables loaded")
    
    # Get configuration
    config = AppConfig.from_env()
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
        
        # Initialize summarizer
        summarizer = PRSummarizer(MODEL_PATH, config.llm_config.dict())
        
        # Process each PR
        logger.info(f"Processing {len(prs)} PRs")
        all_summaries = []
        
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
                logger.info("Generating summary")
                start_time = time.time()
                summary = summarizer.summarize(pr_data)
                duration = time.time() - start_time
                logger.info(f"Summary generated in {duration:.2f} seconds")
                
                # Store summary for later display
                all_summaries.append({
                    'pr_data': pr_data,
                    'summary': summary
                })
                
                progress.update(task, advance=1)
        
        # Display all summaries at once
        display_all_summaries(all_summaries)
        logger.info("All PRs processed successfully")
        
    except Exception as e:
        logger.error(f"Error: {str(e)}", exc_info=True)

if __name__ == "__main__":
    main() 