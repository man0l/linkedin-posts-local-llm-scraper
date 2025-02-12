import asyncio
from typing import List, Optional
from pydantic import BaseModel
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
from crawl4ai.extraction_strategy import LLMExtractionStrategy
import time

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
        provider="ollama/deepseek-r1:7b",  # Updated to use available model
        api_base="http://127.0.0.1:11434",  # Ollama endpoint
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
        chunk_token_threshold=2000,
        overlap_rate=0.1,
        apply_chunking=True,
        input_format="html",  # Using HTML since LinkedIn's structure might be important
        extra_args={
            "temperature": 0.1,
            "max_tokens": 2000
        }
    )

    # Configure the crawler
    browser_config = BrowserConfig(
        headless=False,  # Set to False to see what's happening
        browser_type="chromium",
        chrome_channel="chrome",
        channel="chrome",
        user_data_dir="/home/manol/.config/google-chrome/Person 1"  # Use Person 1 profile
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
    # List of LinkedIn activity URLs to crawl
    linkedin_urls = [
        "https://www.linkedin.com/in/alex-lieberman/recent-activity/all/",
        # Add more LinkedIn activity URLs here
    ]

    results = await crawl_linkedin_activities(linkedin_urls)
    
    # Save results to file
    import json
    with open("linkedin_activities.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    asyncio.run(main()) 