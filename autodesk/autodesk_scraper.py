import os
import sys
import csv
import requests
from bs4 import BeautifulSoup
import concurrent.futures
import time
import random

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(parent_dir)

import scraper_helper

BASE_URL = "https://www.autodesk.com/partners/strategic-alliance-partners"
MAX_THREADS = 5

partners = []


def get_partners(html):
    soup = BeautifulSoup(html, "html.parser")

    elements = soup.find("div", class_="resources-multi-use")    
    if not elements:
        print("*** Failed to find partners")
        scraper_helper.output_soup(soup, "err_autodesk_pg.html")
        return
    
    cards = elements.find_all("div", class_="pnl-rmu__card pnl-rmu__load-more-card md:dhig-col-span-3 lg:dhig-col-span-4")
    if not cards:
        print("*** Failed to find cards")
        scraper_helper.output_soup(elements, "err_autodesk_elements.html")
        return

    for i, card in enumerate(cards):
        name_tag = card.find("h3", class_="cmp-title__text dhig-typography-headline-small")
        blurb_tag = card.find("div", class_="dhig-mb-3")
        link_tag = card.find("a")

        if name_tag and link_tag:
            name = name_tag.get_text(strip=True)
            blurb = blurb_tag.get_text(strip=True) if blurb_tag else ""
            link = link_tag.get("href")

            partners.append({"name": name, "link": link, "text": f"{blurb}:   "})
        else:
            print("*** Failed to find partner info")
            scraper_helper.output_soup(card, f"err_autodesk_card{i}.html")



def get_partner_pg(partner):
    url = partner["link"]
    print(f"Fetching: {url}")

    html = scraper_helper.fetch_page(url)
    # html = scraper_helper.fetch_page_selenium(url)
    if not html:
        print(f" ***** Failed to fetch {partner['name']} at {url}\n")
        return

    soup = BeautifulSoup(html, "html.parser")

    partner_text_tag = soup.find_all("div", class_="cmp-container")[1]
    if not partner_text_tag:
        print(f"***** Failed to get {partner['name']} text\n")
        scraper_helper.output_soup(soup, f"err_autodesk_{partner['name']}.html")
    else:
        partner_text = partner_text_tag.get_text(strip=True)
        partner["text"] += partner_text
        print(f"Got {partner['name']} text.")
    scraper_helper.output_soup(soup, f"err_autodesk_{partner['name']}.html")




def main():
    print(f"Scraping {BASE_URL}...")
    homepage_html = scraper_helper.fetch_page(BASE_URL)
    if not homepage_html:
        print("*** Failed to get partner page.")
        return

    get_partners(homepage_html)
    print(f"Found {len(partners)} partners.\n")

    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        executor.map(get_partner_pg, partners)

    # print("Final Data:\n", partners)
    scraper_helper.output_partners(partners, "autodesk_partners.csv")


if __name__ == "__main__":
    main()
