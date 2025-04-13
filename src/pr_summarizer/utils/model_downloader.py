import os
import requests
import logging
from tqdm import tqdm
from pathlib import Path

logger = logging.getLogger(__name__)

class ModelDownloader:
    """Class for downloading the Mistral model."""
    
    def __init__(self, model_url: str, model_path: str):
        """Initialize the model downloader."""
        self.model_url = model_url
        self.model_path = model_path
        self.model_dir = os.path.dirname(model_path)
        logger.info("ModelDownloader initialized")

    def download(self) -> bool:
        """Download the model if it doesn't exist."""
        if os.path.exists(self.model_path):
            logger.info(f"Model already exists at {self.model_path}")
            return True

        try:
            # Create model directory if it doesn't exist
            os.makedirs(self.model_dir, exist_ok=True)
            
            # Download the model
            logger.info(f"Downloading model from {self.model_url}")
            response = requests.get(self.model_url, stream=True)
            response.raise_for_status()
            
            # Get file size
            total_size = int(response.headers.get('content-length', 0))
            
            # Download with progress bar
            with open(self.model_path, 'wb') as f, tqdm(
                desc="Downloading model",
                total=total_size,
                unit='iB',
                unit_scale=True,
                unit_divisor=1024,
            ) as bar:
                for data in response.iter_content(chunk_size=1024):
                    size = f.write(data)
                    bar.update(size)
            
            logger.info(f"Model downloaded successfully to {self.model_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to download model: {str(e)}")
            if os.path.exists(self.model_path):
                os.remove(self.model_path)
            return False 