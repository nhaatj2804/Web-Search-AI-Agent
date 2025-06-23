import asyncio
from crawl4ai import *
from crawl4ai.content_filter_strategy import BM25ContentFilter
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator

import os

async def getResult(urls, user_request, collection_id: str):
    async with AsyncWebCrawler() as crawler:
         # Step 1: Create a pruning filter
        prune_filter = PruningContentFilter(
            # Lower → more content retained, higher → more content pruned
            threshold=0.45,           
            # "fixed" or "dynamic"
            threshold_type="dynamic",  
            # Ignore nodes with <5 words
            min_word_threshold=5      
        )
        # Step 2: Insert it into a Markdown Generator
        md_generator = DefaultMarkdownGenerator(content_filter=prune_filter)
        # Step 3: Pass it to CrawlerRunConfig
        config = CrawlerRunConfig(
            markdown_generator=md_generator,
            cache_mode=CacheMode.BYPASS,
            stream=False  # Default: get all results at once
        )

        browser_config = BrowserConfig(headless=True, verbose=False)

        dispatcher = MemoryAdaptiveDispatcher(
            memory_threshold_percent=70.0,
            check_interval=1.0,
            max_session_permit=10,
        )
        results = await crawler.arun_many(urls=urls,config=config, dispatcher=dispatcher, browser_config=browser_config)
        # Set up data directory with collection
        data_path = os.path.join("data", collection_id) if collection_id else "data"
        print(collection_id)
        os.makedirs(data_path, exist_ok=True)
        for result in results:
            if result.success:
                # Sanitize the filename by replacing invalid characters
                sanitized_url = result.url
                for char in [":", "/", "\\", "?", "<", ">", "|", "*", '"']:
                    sanitized_url = sanitized_url.replace(char, "_")

                filename = os.path.join(data_path, f"{sanitized_url}.md")
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(result.markdown.fit_markdown)
