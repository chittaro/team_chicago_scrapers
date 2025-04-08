import os
import time
import sys
from urllib.parse import quote
import concurrent
import uuid

import scraper_helper
from url_generator.search_url_gen import get_company_partnership_urls
from name_finder.name_finder import get_html, get_names, get_all_names

########## GET COMPANY NAME ##########
company_name = input("Enter the company name: ").strip()

########## GET URLS ##########
print(f"\n\n********** Getting relevant URLS...")
urls = get_company_partnership_urls(company_name)
print(f"Found {len(urls)} URLs for {company_name} partnerships, first 10:")
for idx, url in enumerate(urls[:10], start=1):
    print(f"{idx}. {url}")

########## GET HTML TEXT ##########
print(f"\n\n********** Fetching {len(urls)} HTML pages...")
pages = get_html(company_name, urls)
print(f"Got {pages} pages")

########## DEMO: GET COMPANY NAMES FROM ONE LINK ##########
# print(f"\n\n********** Getting {company_name} partner names...")
# ex_filename = 'name_finder/16838a97-f8f9-42b4-9502-6c9b89ed679a.txt'
# names = get_names(ex_filename)
# print(f"{company_name} partner names: {names}")

print(f"\n\n********** Getting {company_name} partner names...")
names = get_all_names(company_name)
print(f"{company_name} partner names: {names}")
