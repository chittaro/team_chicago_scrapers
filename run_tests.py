import time
import sys
import os
from test_accuracy.sheets_scraper import write_competitor_data
from url_generator.search_url_gen import get_company_partnership_urls
from name_finder.name_finder import get_html, get_names, get_all_names, clear_html
from test_accuracy.test_accuracy import get_stats, make_partner_count_barchart


######### GET MANUAL DATA #########
## ** only need to run once unless we change sheets data
# write_competitor_data()


######### RUN MAIN PIPELINE #########
# competitors = ["Faro", "Zeiss", "Autodesk", "PTC", "Sandvik", "Altair", "Ansys", "Dassault Systems", "Siemens"]
# for company_name in competitors:
#     start_time = time.time()

#     ## GET URLS ##
#     print(f"\n\n********** Getting relevant URLS for {company_name}...")
#     urls = get_company_partnership_urls(company_name)

#     ## GET HTML ##
#     print(f"\n\n********** Clearing prior html data for {company_name}...")
#     clear_html(company_name)
#     print(f"\n\n********** Fetching HTML pages...")
#     pages = get_html(company_name)

#     ## GET PARTNER NAMES ##
#     print(f"\n\n********** Getting {company_name} partner names...")
#     names = get_all_names(company_name)
#     print(f"{company_name} partner names: {names}")

#     runtime = time.time() - start_time

#     with open("runtimes.txt", "a") as f:
#         f.write(f"{company_name} runtime: {runtime}")
#         print(f"{company_name} runtime: {runtime}")


######### RUN ANALYSIS #########
get_stats("Faro")
# make_partner_count_barchart()