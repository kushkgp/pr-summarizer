import logging
from rich.logging import RichHandler
from dotenv import load_dotenv
import os
from datetime import datetime

from src.config.settings import AppConfig
from src.core.app import PRSummarizerApp

def setup_logging():
    """Configure logging with both file and console handlers."""
    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)
    
    # Create a file handler for detailed logs
    log_file = f"logs/pr_summarizer_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    
    # Create a console handler for minimal output
    console_handler = RichHandler(rich_tracebacks=True, show_time=False, show_path=False)
    console_handler.setLevel(logging.WARNING)  # Only show warnings and errors
    
    # Configure root logger
    logging.basicConfig(
        level=logging.DEBUG,
        handlers=[file_handler, console_handler]
    )

def main():
    """Main entry point for the application."""
    # Setup logging
    setup_logging()
    
    # Load environment variables
    load_dotenv()
    
    try:
        # Initialize configuration
        config = AppConfig()
        config.validate()
        
        # Create and run application
        app = PRSummarizerApp(config)
        app.run()
        
    except Exception as e:
        logging.error(f"Application error: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    main() 