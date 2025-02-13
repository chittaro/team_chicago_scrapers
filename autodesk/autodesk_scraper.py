import requests
from bs4 import BeautifulSoup
import concurrent.futures
import time
import random

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
}

# Rate limit settings
MIN_DELAY = 1
MAX_DELAY = 3
MAX_THREADS = 5

BASE_URL = "https://www.autodesk.com/partners/strategic-alliance-partners"

partners = []


def fetch_page(url):
    try:
        time.sleep(random.uniform(MIN_DELAY, MAX_DELAY))
        response = requests.get(url, headers=HEADERS, timeout=60)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None


def get_partners(html):
    soup = BeautifulSoup(html, "html.parser")
    elements = soup.find(id="group-e8e7a5698f")
    
    if not elements:
        print("No partners section.")
        return
    
    cards = elements.find_all("div", class_="pnl-rmu__card pnl-rmu__load-more-card md:dhig-col-span-3 lg:dhig-col-span-4")

    for card in cards:
        name_tag = card.find("div", class_="dhig-mb-3 dhig-flex dhig-items-center dc-card-flex__title")
        blurb_tag = card.find("div", class_="dhig-mb-3")
        link_tag = card.find("a", class_="cmp-text-link__link MuiTypography-root MuiLink-root MuiLink-underlineHover")

        if name_tag and link_tag:
            name = name_tag.get_text(strip=True)
            blurb = blurb_tag.get_text(strip=True) if blurb_tag else ""
            link = link_tag.get("href")

            partners.append({"name": name, "link": link, "blurb": blurb, "text": ""})


def get_partner_pg(partner):
    url = partner["link"]
    print(f"Fetching: {url}")

    html = fetch_page(url)
    if not html:
        print(f"Failed to fetch {url}")
        return

    soup = BeautifulSoup(html, "html.parser")

    partner_text_tag = soup.find("div", class_="cmp-container")
    partner_text = partner_text_tag.get_text(strip=True) if partner_text_tag else "Error no page text."

    partner["text"] = partner_text
    print(f"Got {partner['name']} text.")


def main():
    print(f"Scraping {BASE_URL}...")
    homepage_html = fetch_page(BASE_URL)
    if not homepage_html:
        print("Failed to get partner page.")
        return

    get_partners(homepage_html)
    print(f"Found {len(partners)} partners.")

    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        executor.map(get_partner_pg, partners)

    print("Final Data:\n", partners)


if __name__ == "__main__":
    main()
