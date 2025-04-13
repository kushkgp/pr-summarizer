# GitHub PR Summarizer

A Python application that fetches and summarizes GitHub pull requests using Mistral's LLM.

## Features

- Fetch recent PRs from any GitHub repository
- Detailed PR summaries using Mistral 7B Instruct model
- Rich console output with progress tracking
- Error handling and logging
- Local LLM processing for privacy and cost efficiency

## Setup

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and fill in your GitHub token:
   ```bash
   cp .env.example .env
   ```
4. Edit `.env` with your GitHub API key:
   ```
   GITHUB_TOKEN=your_github_token_here
   ```

5. Download the Mistral model:
   ```bash
   python3 download_model.py
   ```

## Steps to Run

1. **Environment Setup**
   - Ensure you have Python 3.8 or higher installed
   - Create and activate a virtual environment (recommended):
     ```bash
     python3 -m venv venv
     source venv/bin/activate  # On Windows use: venv\Scripts\activate
     ```

2. **API Keys Setup**
   - Get your GitHub Personal Access Token:
     1. Go to GitHub Settings > Developer Settings > Personal Access Tokens
     2. Generate a new token with `repo` scope
   - Add the token to your `.env` file:
     ```
     GITHUB_TOKEN=your_github_token_here
     ```

3. **Running the Application**
   - Basic usage:
     ```bash
     python3 main.py
     ```
   - The application will prompt you to enter a repository name in the format `owner/repo`
   - Example repository input:
     ```
     octocat/Hello-World
     ```

## Usage

1. Run the application:
   ```bash
   python3 main.py
   ```

2. When prompted, enter the repository name in the format `owner/repo`

3. The application will:
   - Fetch the 10 most recent PRs from the repository
   - Generate summaries using the Mistral model
   - Display results in a formatted table with progress tracking

## Configuration

The application can be configured through environment variables:

- `GITHUB_TOKEN`: Your GitHub personal access token

LLM settings can be modified in the `config.py` file.

## Requirements

- Python 3.8+
- See `requirements.txt` for package dependencies
- ~4.1GB of disk space for the Mistral model
- Sufficient RAM for running the LLM locally

## Notes

- The application uses the Mistral 7B Instruct model in 4-bit quantization for efficient local processing
- PR summaries are generated using the local model, ensuring privacy and reducing API costs
- The application fetches the 10 most recent PRs by default 