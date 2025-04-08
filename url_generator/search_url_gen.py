import requests
import os
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")
if not GOOGLE_API_KEY:
    raise ValueError("Add your Google API key to your .env file.")
if not GOOGLE_CSE_ID:
    raise ValueError("Add your Google Custom Search Engine ID to your .env file.")

def google_search(query, num_results=10):
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "q": query,
        "key": GOOGLE_API_KEY,
        "cx": GOOGLE_CSE_ID,
        "num": num_results
    }

    response = requests.get(url, params=params)
    results = response.json()

    # Extract URLs from search results
    urls = [item["link"] for item in results.get("items", [])]
    return urls

def get_company_partnership_urls(company_name):
    queries = [
        f"{company_name} partners list",
        f"{company_name} official partner companies",
        f"{company_name} strategic alliances"
    ]

    all_urls = set()

    for query in queries:
        urls = google_search(query)
        all_urls.update(urls)

    # TODO: filter URLS

    # write to file
    data_dir = os.path.join("data", company_name)
    os.makedirs(data_dir, exist_ok=True)

    url_file_path = os.path.join(data_dir, "urls.txt")
    if urls:
        with open(url_file_path, "w", encoding="utf-8") as file:
            for url in urls:
                file.write(url + "\n")
        print(f"\nRelevant URLs saved to {url_file_path}")
    else:
        print("No relevant URLs found.")

    # return list(all_urls)[:s20]
    return list(all_urls)


