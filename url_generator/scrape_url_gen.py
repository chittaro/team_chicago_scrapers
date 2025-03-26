import requests
from bs4 import BeautifulSoup
import time
import random
import sys
import os

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(parent_dir)
import scraper_helper

def google_search(query, num_results=5):
    """ Google search a query and return top results """
    search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
    # headers = {
    #     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    # }
    
    # response = requests.get(search_url, headers=headers)
    # if response.status_code != 200:
    #     print(f"Search failed {response.status_code}")
    #     return []
    
    # soup = BeautifulSoup(response.text, "html.parser")
    soup = BeautifulSoup(scraper_helper.fetch_page_selenium(search_url), "html.parser")
    search_results = []
    
    links = soup.find_all('a', href=True)
    if not links:
        print(f"No links found:\n\n{soup}")
        return []
    
    for g in links:
        link = g['href']
        print(f"   link: {link}")
        if "http" in link and not ("webcache" or "/search?") in link:
            # actual_url = link.split("url?q=")[1].split("&")[0]
            search_results.append(link)
        if len(search_results) >= num_results:
            break
    
    return search_results


def get_partner_urls(company_name):
    """ Try different searches for potential partner page URLs """
    queries = [
        f"{company_name} partners list",
        f"{company_name} official partner companies",
        f"{company_name} strategic alliances",
        f"{company_name} reseller partners"
    ]
    
    urls = set()
    for query in queries:
        search_results = google_search(query)
        urls.update(search_results)
        time.sleep(random.uniform(1, 3))  # rate limiting
    
    if urls:
        output_file=f"{company_name}_urls.txt"
        with open(output_file, "w") as file:
            for url in urls:
                file.write(url + "\n")
        print(f"\nRelevant URLs saved to {output_file}")
    else:
        print("No relevant URLs found.")
    return urls

if __name__ == "__main__":
    company = input("Enter company name: ")
    get_partner_urls(company)
