import os
import time
import sys
from urllib.parse import quote
import concurrent
import uuid

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(parent_dir)
from scraper_helper import fetch_page
# from url_generator.search_url_gen import get_company_partnership_urls


def write_html_to_file(company_name, url, html):
    folder_path = os.path.join("data", company_name)
    os.makedirs(folder_path, exist_ok=True)
    unique_id = str(uuid.uuid4())
    filename = os.path.join(folder_path, f"{unique_id}.txt")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"{url}\n\n{html}")
    print(f"Saved: {filename}")

# def get_html(company_name, urls):
#     def process(url):
#         html = fetch_page(url)
#         if html:
#             write_html_to_file(company_name, url, html)
#         else:
#             print(f"Failed: {url}")

#     with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
#         executor.map(process, urls)

def get_html(company_name, urls):
    def process(url):
        html = fetch_page(url)
        if html:
            write_html_to_file(company_name, url, html)
            return 1
        else:
            print(f"Failed: {url}")
            return 0

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        results = list(executor.map(process, urls))

    return sum(results)