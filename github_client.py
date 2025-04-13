from typing import List, Dict, Any, Optional
import requests
from datetime import datetime, timedelta
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeRemainingColumn
from rich.logging import RichHandler
import logging
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichHandler(rich_tracebacks=True)]
)
logger = logging.getLogger("github_client")

console = Console()

class GitHubClient:
    def __init__(self, token: str):
        self.token = token
        self.headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }
        logger.info("GitHub client initialized")
    
    def _log_api_call(self, method: str, url: str, params: Optional[Dict] = None):
        """Log API call details before making the request."""
        logger.info(f"Making {method} request to: {url}")
        if params:
            logger.info(f"Request parameters: {params}")
        logger.info("Starting API call...")
    
    def _log_api_response(self, response, start_time: float):
        """Log API response details."""
        duration = time.time() - start_time
        logger.info(f"API call completed in {duration:.2f} seconds")
        logger.info(f"Response status: {response.status_code}")
        if response.status_code != 200:
            logger.error(f"Error response: {response.text}")
    
    def get_recent_prs(self, repo: str, count: int = 10) -> List[Dict[str, Any]]:
        """Get recent PRs from a repository."""
        logger.info(f"Fetching {count} most recent PRs from {repo}")
        
        url = f"https://api.github.com/repos/{repo}/pulls"
        params = {
            "state": "all",
            "sort": "created",
            "direction": "desc",
            "per_page": count
        }
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            TimeRemainingColumn(),
            console=console
        ) as progress:
            # Fetch PRs
            task = progress.add_task(f"[cyan]Fetching PRs from {repo}...", total=1)
            
            # Log API call
            self._log_api_call("GET", url, params)
            start_time = time.time()
            response = requests.get(url, headers=self.headers, params=params)
            self._log_api_response(response, start_time)
            
            progress.update(task, completed=1)
            
            if response.status_code != 200:
                logger.error(f"Failed to fetch PRs: {response.status_code}")
                return []
            
            prs = response.json()
            logger.info(f"Found {len(prs)} PRs")
            
            # Process each PR
            pr_data_list = []
            task = progress.add_task("[cyan]Processing PRs...", total=len(prs))
            
            for pr in prs:
                # Get PR comments
                logger.info(f"Fetching comments for PR #{pr['number']}")
                self._log_api_call("GET", pr['comments_url'])
                start_time = time.time()
                comments_response = requests.get(pr['comments_url'], headers=self.headers)
                self._log_api_response(comments_response, start_time)
                
                comments = comments_response.json() if comments_response.status_code == 200 else []
                
                pr_data = {
                    'title': pr['title'],
                    'repository_url': pr['html_url'],
                    'created_at': pr['created_at'],
                    'state': pr['state'],
                    'number': pr['number'],
                    'body': pr['body'],
                    'comments': [c['body'] for c in comments]
                }
                pr_data_list.append(pr_data)
                progress.update(task, advance=1)
            
            logger.info(f"Successfully processed {len(pr_data_list)} PRs")
            return pr_data_list

    def get_pr_data(self, repo: str, pr_number: str) -> Dict[str, Any]:
        """Get PR data from GitHub API."""
        logger.info(f"Fetching PR #{pr_number} from {repo}")
        
        url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}"
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            TimeRemainingColumn(),
            console=console
        ) as progress:
            # Fetch PR details
            task = progress.add_task("[cyan]Fetching PR details...", total=1)
            
            # Log API call
            self._log_api_call("GET", url)
            start_time = time.time()
            response = requests.get(url, headers=self.headers)
            self._log_api_response(response, start_time)
            
            progress.update(task, completed=1)
            
            if response.status_code != 200:
                logger.error(f"Failed to fetch PR data: {response.status_code}")
                return {}
            
            pr_data = response.json()
            
            # Get PR comments
            task = progress.add_task("[cyan]Fetching PR comments...", total=1)
            
            # Log API call
            self._log_api_call("GET", pr_data['comments_url'])
            start_time = time.time()
            comments_response = requests.get(pr_data['comments_url'], headers=self.headers)
            self._log_api_response(comments_response, start_time)
            
            progress.update(task, completed=1)
            
            comments = comments_response.json() if comments_response.status_code == 200 else []
            
            logger.info(f"Successfully fetched PR #{pr_number} with {len(comments)} comments")
            
            return {
                'title': pr_data['title'],
                'repository_url': pr_data['html_url'],
                'created_at': pr_data['created_at'],
                'state': pr_data['state'],
                'body': pr_data['body'],
                'comments': [c['body'] for c in comments]
            }

# Keep the utility functions for backward compatibility
def create_headers(token: str) -> Dict[str, str]:
    return {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }

def get_prs_for_user(username: str, token: str, days: int) -> List[Dict[str, Any]]:
    logger.info(f"Fetching PRs for user {username} in the last {days} days")
    
    headers = create_headers(token)
    since_date = (datetime.now() - timedelta(days=days)).isoformat()
    url = f"https://api.github.com/search/issues"
    
    params = {
        "q": f"author:{username} type:pr created:>={since_date}",
        "sort": "created",
        "order": "desc"
    }
    
    all_prs = []
    page = 1
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        TimeRemainingColumn(),
        console=console
    ) as progress:
        task = progress.add_task("[cyan]Fetching PRs...", total=None)
        
        while True:
            params["page"] = page
            logger.info(f"Fetching page {page} of PRs")
            self._log_api_call("GET", url, params)
            start_time = time.time()
            response = requests.get(url, headers=headers, params=params)
            self._log_api_response(response, start_time)
            
            if response.status_code != 200:
                logger.error(f"Failed to fetch PRs: {response.status_code}")
                break
                
            data = response.json()
            prs = data.get("items", [])
            
            if not prs:
                break
                
            all_prs.extend(prs)
            page += 1
            
            progress.update(task, advance=len(prs))
    
    logger.info(f"Found {len(all_prs)} PRs for user {username}")
    return all_prs

def get_pr_details(pr_url: str, token: str) -> Dict[str, Any]:
    logger.info(f"Fetching PR details from {pr_url}")
    
    headers = create_headers(token)
    self._log_api_call("GET", pr_url)
    start_time = time.time()
    response = requests.get(pr_url, headers=headers)
    self._log_api_response(response, start_time)
    
    if response.status_code != 200:
        logger.error(f"Failed to fetch PR details: {response.status_code}")
        return {}
        
    return response.json()

def get_pr_comments(comments_url: str, token: str) -> List[Dict[str, Any]]:
    logger.info(f"Fetching PR comments from {comments_url}")
    
    headers = create_headers(token)
    self._log_api_call("GET", comments_url)
    start_time = time.time()
    response = requests.get(comments_url, headers=headers)
    self._log_api_response(response, start_time)
    
    if response.status_code != 200:
        logger.error(f"Failed to fetch PR comments: {response.status_code}")
        return []
        
    return response.json() 