import os
import time
import sys
from urllib.parse import quote
import concurrent
import uuid

import scraper_helper
from url_generator.search_url_gen import get_company_partnership_urls
from name_finder.name_finder import get_html


company_name = input("Enter the company name: ").strip()

urls = get_company_partnership_urls(company_name)

print(f"\nTop 10 real URLs for {company_name} partnerships:")
for idx, url in enumerate(urls[:10], start=1):
    print(f"{idx}. {url}")

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

print(f"\nFetching {len(urls)} HTML pages...")
pages = get_html(company_name, urls)
print(f"Got {pages} pages")