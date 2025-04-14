from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import requests
from rich.console import Console
from rich.progress import Progress
import logging

logger = logging.getLogger(__name__)
console = Console()

class GitHubClient:
    """Client for interacting with GitHub API."""
    
    def __init__(self, token: str):
        """Initialize GitHub client with authentication token."""
        self.token = token
        self.headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }
        self.base_url = "https://api.github.com"
        logger.debug("GitHub client initialized")

    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Any:
        """Make a request to GitHub API."""
        url = f"{self.base_url}/{endpoint}"
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"GitHub API request failed: {str(e)}")
            raise

    def get_recent_prs(self, repo: str, days: int = 7) -> List[Dict[str, Any]]:
        """Get recent pull requests for a repository."""
        owner, repo_name = repo.split('/')
        since = (datetime.now() - timedelta(days=days)).isoformat()
        
        endpoint = f"repos/{owner}/{repo_name}/pulls"
        params = {
            "state": "all",
            "sort": "created",
            "direction": "desc",
            "since": since
        }
        
        try:
            logger.info(f"Fetching PRs from {repo}")
            prs = self._make_request(endpoint, params)
            logger.info(f"Found {len(prs)} PRs")
            return [
                {
                    "number": pr["number"],
                    "title": pr["title"],
                    "body": pr["body"],
                    "state": pr["state"],
                    "created_at": pr["created_at"],
                    "repository_url": pr["base"]["repo"]["html_url"],
                    "user": pr["user"]["login"]
                }
                for pr in prs
            ]
        except Exception as e:
            logger.error(f"Failed to fetch PRs: {str(e)}")
            return [] 