# GitHub PR Summarizer

A Python application that fetches and summarizes GitHub pull requests using OpenAI's LLM.

## Features

- Fetch PRs for a specific user within a given time period
- Detailed PR summaries using OpenAI's LLM
- Console or file output options
- Progress tracking for API calls
- Error handling and logging

## Setup

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and fill in your API keys:
   ```bash
   cp .env.example .env
   ```
4. Edit `.env` with your GitHub and OpenAI API keys

## Steps to Run

1. **Environment Setup**
   - Ensure you have Python 3.8 or higher installed
   - Create and activate a virtual environment (recommended):
     ```bash
     python -m venv venv
     source venv/bin/activate  # On Windows use: venv\Scripts\activate
     ```

2. **API Keys Setup**
   - Get your GitHub Personal Access Token:
     1. Go to GitHub Settings > Developer Settings > Personal Access Tokens
     2. Generate a new token with `repo` scope
   - Get your OpenAI API Key:
     1. Sign up at OpenAI
     2. Create an API key in your account settings
   - Add these keys to your `.env` file:
     ```
     GITHUB_TOKEN=your_github_token_here
     OPENAI_API_KEY=your_openai_key_here
     ```

3. **Running the Application**
   - Basic usage (console output):
     ```bash
     python main.py <github_username> <days_to_look_back>
     ```
   - Example to get PRs from the last 7 days:
     ```bash
     python main.py octocat 7
     ```
   - To save output to a file:
     ```bash
     python main.py octocat 7 --output file --output-file summaries.json
     ```

4. **Verification**
   - Check the console output or the generated file for PR summaries
   - Ensure you see progress indicators for API calls
   - Verify that PR summaries are being generated correctly

## Usage

Basic usage:
```bash
python main.py <github_username> <days_to_look_back>
```

Example:
```bash
python main.py octocat 7
```

### Options

- `--output`: Output format (console or file)
- `--output-file`: Output file path (required if output is file)

Example with file output:
```bash
python main.py octocat 7 --output file --output-file summaries.json
```

## Configuration

The application can be configured through environment variables:

- `GITHUB_TOKEN`: Your GitHub personal access token
- `OPENAI_API_KEY`: Your OpenAI API key

LLM settings can be modified in the `config.py` file.

## Requirements

- Python 3.8+
- See `requirements.txt` for package dependencies 