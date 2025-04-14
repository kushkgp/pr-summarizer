import os
import json
from typing import Dict, Any
from dotenv import load_dotenv

def load_config() -> Dict[str, Any]:
    """Load configuration from config.json file and environment variables."""
    # Load environment variables
    load_dotenv()
    
    config_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "config.json")
    
    if not os.path.exists(config_path):
        # Create default config if it doesn't exist
        default_config = {
            "github": {
                "token": os.getenv("GITHUB_TOKEN"),
                "repo": "kushagra-kag/pr-summarizer"  # Default repository
            },
            "model": {
                "path": "models/mistral-7b-instruct-v0.2.Q4_K_M.gguf",
                "context_window": 4096,
                "temperature": 0.7,
                "top_p": 0.95,
                "repeat_penalty": 1.1
            },
            "batch_size": 5
        }
        
        with open(config_path, "w") as f:
            json.dump(default_config, f, indent=4)
        
        return default_config
    
    # Load config from file
    with open(config_path, "r") as f:
        config = json.load(f)
    
    # Override token from environment if available
    if "GITHUB_TOKEN" in os.environ:
        config["github"]["token"] = os.getenv("GITHUB_TOKEN")
    
    return config 