import os
import time
import sys
from urllib.parse import quote
import concurrent
import uuid

# import scraper_helper
from url_generator.search_url_gen import get_company_partnership_urls
# swap these in for partner type and domain
# from name_finder.name_finder import get_html, get_names, get_all_names, clear_html
# from name_finder.name_type_finder import get_html, get_names, get_all_names, clear_html
from name_finder.name_type_domain_finder import get_html, get_names, get_all_names, clear_html

# note to gang: each of these sections can run independently, just comment out any steps you 
# don't want to be run again (get html uses hella search api and get partner names uses hella openai)
# and it will use the old values in data/


########## GET COMPANY NAME ##########
company_name = input("Enter the company name: ").strip()


########## GET URLS ##########
# print(f"\n\n********** Getting relevant URLS...")
# urls = get_company_partnership_urls(company_name)
# print(f"Found {len(urls)} URLs for {company_name} partnerships, first 10:")
# for idx, url in enumerate(urls[:10], start=1):
#     print(f"{idx}. {url}")


########## GET HTML TEXT ##########
# print(f"\n\n********** Clearing prior html data for {company_name}...")
# clear_html(company_name)
# print(f"\n\n********** Fetching HTML pages...")
# pages = get_html(company_name)
# print(f"Got {pages} pages")


# ########## OLD DEMO: GET COMPANY NAMES FROM ONE LINK ##########
# # print(f"\n\n********** Getting {company_name} partner names...")
# # ex_filename = 'name_finder/16838a97-f8f9-42b4-9502-6c9b89ed679a.txt'
# # names = get_names(ex_filename)
# # print(f"{company_name} partner names: {names}")


########## GET PARTNER NAMES ##########
print(f"\n\n********** Getting {company_name} partner names and partnership types...")
names = get_all_names(company_name)
print(f"{company_name} partner names: {names}")


########## GET PARTER INFO ##########
# TODO
