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
        logger.debug("PRSummarizerApp initialized")

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
        console.print("[bold cyan]GitHub PR Summarizer[/bold cyan]")
        
        try:
            repo = self.get_repo_input()
            
            with console.status("[bold green]Fetching PRs...[/bold green]") as status:
                prs = self.github_client.get_recent_prs(repo)
                if not prs:
                    console.print("[bold red]No PRs found or failed to fetch PRs[/bold red]")
                    return
            
            console.print(f"[bold green]Found {len(prs)} PRs to summarize[/bold green]")
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
                TimeRemainingColumn(),
                console=console
            ) as progress:
                task = progress.add_task("[cyan]Summarizing PRs...", total=len(prs))
                
                # Make a single call to the LLM for all PRs
                start_time = time.time()
                summaries = self.summarizer.summarize_all(prs)
                duration = time.time() - start_time
                logger.debug(f"All summaries generated in {duration:.2f} seconds")
                
                # Display results
                for pr_data, summary in zip(prs, summaries):
                    self.display_pr_summary(pr_data, summary)
                    progress.update(task, advance=1)
            
            console.print("[bold green]All PRs processed successfully[/bold green]")
            
        except Exception as e:
            console.print(f"[bold red]Error: {str(e)}[/bold red]")
            logger.error(f"Error: {str(e)}", exc_info=True) 