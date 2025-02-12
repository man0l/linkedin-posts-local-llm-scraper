# LinkedIn Activity Crawler

A Python script that crawls LinkedIn activity feeds and extracts structured data using LLM-based extraction.

## Prerequisites

- Python 3.8 or higher
- Google Chrome browser installed
- Ollama running locally with the deepseek-r1:7b model

## Installation

1. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Linux/Mac
# or
.venv\Scripts\activate  # On Windows
```

2. Install the requirements:
```bash
pip install -r requirements.txt
```

3. Copy the example environment file and configure it:
```bash
cp .env.example .env
```

4. Edit the `.env` file with your settings:
- Set `CHROME_PROFILE_DIR` to your Chrome profile directory
- Configure the LLM settings if needed
- Add LinkedIn URLs to crawl

## Usage

1. Make sure Ollama is running with the deepseek-r1:7b model:
```bash
ollama run deepseek-r1:7b
```

2. Run the crawler:
```bash
python linkedin_crawler.py
```

The script will:
1. Open Chrome using your specified profile
2. Visit each LinkedIn URL
3. Extract activity data using the LLM
4. Save results to `linkedin_activities.json`

## Configuration

The following settings can be configured in the `.env` file:

### Browser Settings
- `BROWSER_TYPE`: Browser type (default: chromium)
- `CHROME_CHANNEL`: Chrome channel (default: chrome)
- `BROWSER_HEADLESS`: Run in headless mode (default: false)
- `CHROME_PROFILE_DIR`: Path to Chrome profile directory

### LLM Settings
- `LLM_PROVIDER`: Ollama model to use
- `LLM_API_BASE`: Ollama API endpoint
- `LLM_TEMPERATURE`: Model temperature
- `LLM_MAX_TOKENS`: Maximum tokens for completion
- `LLM_CHUNK_THRESHOLD`: Token threshold for chunking
- `LLM_OVERLAP_RATE`: Overlap rate for chunking

### URLs
- `LINKEDIN_URLS`: Comma-separated list of LinkedIn activity URLs to crawl 