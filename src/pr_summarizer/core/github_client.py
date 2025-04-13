import requests
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from rich.progress import Progress
from rich.console import Console

logger = logging.getLogger(__name__)
console = Console()

class GitHubClient:
    """Client for interacting with the GitHub API."""
    
    def __init__(self, token: str):
        """Initialize the GitHub client with an API token."""
        self.token = token
        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }
        logger.info("GitHub client initialized")

    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """Make a request to the GitHub API."""
        url = f"{self.base_url}{endpoint}"
        logger.info(f"Making GET request to: {url}")
        logger.info(f"Request parameters: {params}")
        
        logger.info("Starting API call...")
        start_time = datetime.now()
        response = requests.get(url, headers=self.headers, params=params)
        duration = (datetime.now() - start_time).total_seconds()
        logger.info(f"API call completed in {duration:.2f} seconds")
        logger.info(f"Response status: {response.status_code}")

        if response.status_code != 200:
            logger.error(f"Error response: {response.text}")
            raise Exception(f"Failed to fetch data: {response.status_code}")

        return response.json()

    def get_recent_prs(self, repo: str, count: int = 10) -> List[Dict[str, Any]]:
        """Get recent pull requests for a repository."""
        owner, repo_name = repo.split('/')
        logger.info(f"Fetching {count} most recent PRs from {repo}")
        
        with Progress() as progress:
            task = progress.add_task(f"Fetching PRs from {repo}...", total=1)
            
            try:
                prs = self._make_request(
                    f"/repos/{owner}/{repo_name}/pulls",
                    params={
                        "state": "all",
                        "sort": "created",
                        "direction": "desc",
                        "per_page": count
                    }
                )
                progress.update(task, completed=1)
                logger.info(f"Found {len(prs)} PRs")
                return prs
            except Exception as e:
                logger.error(f"Failed to fetch PRs: {str(e)}")
                progress.update(task, completed=1)
                return [] 