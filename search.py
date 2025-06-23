import requests
from get_result import getResult
import asyncio
import os
from dotenv import load_dotenv
from model import process
from create_database import split_documents, save_to_chroma, load_documents
from query import query
import time

# Load environment variables from .env file
load_dotenv()

def google_search(query, api_key, cse_id, num_results=3, exclude_sites=None):
    # Default excluded sites
    default_exclusions = ["facebook.com", "youtube.com", "reddit.com","bbc.com"]
    exclude_sites = exclude_sites or default_exclusions

    # Add -site: exclusions to query
    for site in exclude_sites:
        query += f" -site:{site}"

    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "q": query,
        "key": api_key,
        "cx": cse_id,
        "num": num_results,
        "gl": "vn"          # prefer results from Vietnam
    }

    response = requests.get(url, params=params)
    results = response.json()

    search_results = []
    for item in results.get("items", []):
        search_results.append({
            "title": item.get("title"),
            "link": item.get("link"),
            "snippet": item.get("snippet"),
        })

    return search_results