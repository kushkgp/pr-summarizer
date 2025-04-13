import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "src")))

from pr_summarizer.main import main

if __name__ == "__main__":
    main() 