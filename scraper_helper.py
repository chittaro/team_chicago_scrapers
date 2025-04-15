import csv
import requests
from bs4 import BeautifulSoup
import concurrent.futures
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import time
import random
import brotli

# HEADERS = {
#     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
# }
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Connection": "keep-alive",
}

# Rate limit settings
MIN_DELAY = 1
MAX_DELAY = 3
MAX_THREADS = 5

# partners = [{"name": x, "link": y, "text": z}, ...]

def fetch_page(url):
    try:
        # time.sleep(random.uniform(MIN_DELAY, MAX_DELAY))    # comment out if no rate limiting
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()

        # content_encoding = response.headers.get("Content-Encoding", "")
        # print(f"Found {content_encoding} type page.")
        # if "br" in content_encoding:
        #     try:
        #         html_content = brotli.decompress(response.content).decode("utf-8", errors="replace")
        #     except brotli.error:
        #         # print("* Brotli decompression failed, falling back to response.text")
        #         html_content = response.text
        # elif "gzip" in content_encoding or "deflate" in content_encoding:
        #     html_content = response.content.decode("utf-8", errors="replace")
        # else:
        #     html_content = response.text  # default handling

        return response.text
    
    except requests.RequestException as e:
        print(f"* Error fetching {url}: {e}")
        return None
    
def fetch_page_selenium(url):
    options = Options()
    options.headless = True
    options.add_argument("--disable-blink-features=AutomationControlled")  # for bot detection
    options.add_argument("start-maximized")
    options.add_argument("--disable-infobars")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        driver.get(url)
        page_source = driver.page_source
        return page_source
    except Exception as e:
        print(f"* Error fetching {url} (Selenium): {e}")
        return None
    finally:
        driver.quit()


def output_soup(soup, filename):
    with open(filename, "w", encoding="utf-8") as file:
        file.write(soup.prettify())
    print(f"Soup written to {filename}")

def output_partners(partner_list, filename):
    fieldnames = partner_list[0].keys()
    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(partner_list)

    print(f"Partners written to {filename}")
