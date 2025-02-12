import asyncio
from typing import List, Optional
from pydantic import BaseModel
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
from crawl4ai.extraction_strategy import LLMExtractionStrategy
import time
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class LinkedInActivity(BaseModel):
    activity_type: str  # post, share, comment, etc
    content: str
    timestamp: Optional[str]
    engagement: Optional[dict]  # likes, comments, etc

class LinkedInProfile(BaseModel):
    profile_url: str
    activities: List[LinkedInActivity]

async def crawl_linkedin_activities(urls: List[str]) -> List[dict]:
    # Define LLM extraction strategy using Ollama
    llm_strategy = LLMExtractionStrategy(
        provider=os.getenv("LLM_PROVIDER"),
        api_base=os.getenv("LLM_API_BASE"),
        schema=LinkedInProfile.model_json_schema(),
        extraction_type="schema",
        instruction="""
        Extract LinkedIn profile activities from the page content.
        For each activity, identify:
        - The type of activity (post, share, comment)
        - The main content text
        - Timestamp if available
        - Any engagement metrics (likes, comments) if visible
        Return the data in valid JSON format matching the schema.
        """,
        chunk_token_threshold=int(os.getenv("LLM_CHUNK_THRESHOLD", "2000")),
        overlap_rate=float(os.getenv("LLM_OVERLAP_RATE", "0.1")),
        apply_chunking=True,
        input_format="html",  # Using HTML since LinkedIn's structure might be important
        extra_args={
            "temperature": float(os.getenv("LLM_TEMPERATURE", "0.1")),
            "max_tokens": int(os.getenv("LLM_MAX_TOKENS", "2000"))
        }
    )

    # Configure the crawler
    browser_config = BrowserConfig(
        headless=os.getenv("BROWSER_HEADLESS", "false").lower() == "true",
        browser_type=os.getenv("BROWSER_TYPE", "chromium"),
        chrome_channel=os.getenv("CHROME_CHANNEL", "chrome"),
        channel=os.getenv("CHROME_CHANNEL", "chrome"),
        user_data_dir=os.getenv("CHROME_PROFILE_DIR")
    )

    crawl_config = CrawlerRunConfig(
        extraction_strategy=llm_strategy,
        cache_mode=CacheMode.BYPASS
    )

    results = []
    
    async with AsyncWebCrawler(config=browser_config) as crawler:
        for url in urls:
            try:
                print(f"Crawling: {url}")
                result = await crawler.arun(url=url, config=crawl_config)
                
                if result.success:
                    results.append(result.extracted_content)
                    print(f"Successfully crawled: {url}")
                    llm_strategy.show_usage()  # Show token usage stats
                else:
                    print(f"Failed to crawl {url}: {result.error_message}")
                
                # Add delay between requests
                time.sleep(3)
            
            except Exception as e:
                print(f"Error processing {url}: {str(e)}")
                continue

    return results

async def main():
    # Get LinkedIn URLs from environment
    linkedin_urls = [url.strip() for url in os.getenv("LINKEDIN_URLS", "").split(",")]
    if not linkedin_urls or not linkedin_urls[0]:
        raise ValueError("No LinkedIn URLs provided in LINKEDIN_URLS environment variable")

    results = await crawl_linkedin_activities(linkedin_urls)
    
    # Save results to file
    import json
    with open("linkedin_activities.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    asyncio.run(main()) 