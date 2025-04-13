from typing import List, Dict, Any
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeRemainingColumn
import logging
import time

from src.config.settings import AppConfig
from src.core.github import GitHubClient
from src.core.summarizer import LLMSummarizer

logger = logging.getLogger(__name__)
console = Console()

class PRSummarizerApp:
    """Main application class for PR summarization."""
    
    def __init__(self, config: AppConfig):
        """Initialize the application with configuration."""
        self.config = config
        self.github_client = GitHubClient(config.github_token)
        self.summarizer = LLMSummarizer(config.llm_config)

    def get_repo_input(self) -> str:
        """Get repository name from user input."""
        return Prompt.ask("Enter GitHub repository (owner/repo)")

    def display_pr_summary(self, pr_data: Dict[str, Any], summary: str) -> None:
        """Display PR information and summary in a formatted way."""
        table = Table(title=f"PR #{pr_data.get('number', 'N/A')} Information", show_header=True, header_style="bold magenta")
        table.add_column("Field", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Title", pr_data.get('title', 'N/A'))
        table.add_row("Repository", pr_data.get('repository_url', 'N/A'))
        table.add_row("Created At", pr_data.get('created_at', 'N/A'))
        table.add_row("Status", pr_data.get('state', 'N/A'))
        
        console.print(table)
        console.print("\n")
        console.print(Panel(summary, title="PR Summary", border_style="blue"))
        console.print("\n" + "="*80 + "\n")

    def run(self) -> None:
        """Run the PR summarization process."""
        logger.info("Starting PR Summarizer")
        
        try:
            repo = self.get_repo_input()
            logger.info(f"Selected repository: {repo}")
            
            prs = self.github_client.get_recent_prs(repo)
            if not prs:
                logger.error("No PRs found or failed to fetch PRs")
                return
            
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
                    
                    start_time = time.time()
                    summary = self.summarizer.summarize(pr_data)
                    duration = time.time() - start_time
                    logger.info(f"LLM summary generated in {duration:.2f} seconds")
                    
                    self.display_pr_summary(pr_data, summary)
                    progress.update(task, advance=1)
            
            logger.info("All PRs processed successfully")
            
        except Exception as e:
            logger.error(f"Error: {str(e)}", exc_info=True) 