import logging
from pr_summarizer.utils.model_downloader import ModelDownloader

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

def main():
    """Download the Mistral model if it doesn't exist."""
    model_url = "https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/resolve/main/mistral-7b-instruct-v0.2.Q4_K_M.gguf"
    model_path = "models/mistral-7b-instruct-v0.2.Q4_K_M.gguf"
    
    downloader = ModelDownloader(model_url, model_path)
    success = downloader.download()
    
    if success:
        logger.info("Model download completed successfully")
    else:
        logger.error("Failed to download model")

if __name__ == "__main__":
    main() 