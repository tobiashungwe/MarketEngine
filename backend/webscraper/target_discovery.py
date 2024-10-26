# target_discovery.py

import os
from googleapiclient.discovery import build
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Retrieve API key and CSE ID from environment
API_KEY = os.getenv("GOOGLE_API_KEY")
CSE_ID = os.getenv("GOOGLE_CSE_ID")

def google_search(query, api_key=API_KEY, cse_id=CSE_ID, num_results=10):
    """Search Google and return a list of URLs based on the query."""
    service = build("customsearch", "v1", developerKey=api_key)
    result = service.cse().list(q=query, cx=cse_id, num=num_results).execute()
    urls = [item['link'] for item in result.get('items', [])]
    return urls

def find_target_companies(industry="technology", location="USA", max_results=10):
    """Find companies based on industry and location."""
    query = f"{industry} companies in {location}"
    print(f"Searching for: {query}")
    return google_search(query, num_results=max_results)
