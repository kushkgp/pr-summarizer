import logging
from rich.logging import RichHandler
from dotenv import load_dotenv

from src.config.settings import AppConfig
from src.core.app import PRSummarizerApp

def main():
    """Main entry point for the application."""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s",
        handlers=[RichHandler(rich_tracebacks=True)]
    )
    
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