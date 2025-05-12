import json
import os
import time
import sys
from urllib.parse import quote
import hashlib
from urllib.parse import urlparse
import concurrent
import uuid
import openai
import re
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from collections import defaultdict, Counter
from datetime import datetime



parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(parent_dir)

WORKING_DIR = os.path.abspath(os.path.dirname(__file__))
DATA_DIR = os.path.abspath(os.path.join(WORKING_DIR, "..", "data"))
from scraper_helper import fetch_page , fetch_page_selenium

enable_selenium = False

env_path = os.path.join(parent_dir, ".env")
load_dotenv(dotenv_path=env_path)
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("Add your OpenAI key to your .env file.")

client = openai.OpenAI(api_key=api_key)



def write_text_to_file(company_name, url, text):
    company_name = company_name.lower()
    folder_path = os.path.join("data", company_name)
    os.makedirs(folder_path, exist_ok=True)
    unique_id = str(uuid.uuid4())
    filename = os.path.join(folder_path, f"data_{unique_id}.txt")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"{url}\n\n{text}")
    print(f"Saved: {filename}")


def get_html(company_name):
    # load urls from file (already filtered)
    company_name = company_name.lower()
    urls_file = os.path.join("data", company_name, "urls.txt")
    with open(urls_file, "r") as f:
        urls = [line.strip() for line in f if line.strip()]

    def process(url):
        html = fetch_page(url)
        if html:
            soup = BeautifulSoup(html, "html.parser")
            text = soup.get_text(separator="\n", strip=True)
            write_text_to_file(company_name, url, text)
            return 1
        elif enable_selenium:
            print(f"Trying Selenium: {url}")
            html = fetch_page_selenium(url)
            if html:
                soup = BeautifulSoup(html, "html.parser")
                text = soup.get_text(separator="\n", strip=True)
                write_text_to_file(company_name, url, text)
                return 1
            else:
                print(f"FAILED Selenium: {url}")
                write_text_to_file(company_name, url, "Failed to get page.")
        else:
            print(f"Failed to get page: {url}")
            write_text_to_file(company_name, url, "Failed to get page.")
            return 0


    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        results = list(executor.map(process, urls))

    return sum(results)


def chunk_text(text, max_length=6000, overlap=500):
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        end = min(len(words), start + max_length)
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        start += max_length - overlap
    if len(chunks) > 5:
        print(f"WARNING: text too long, {len(chunks)} chunks truncated to 5.")
    return chunks[:5]  # limiting this to 5 chunks lmao @bella

def get_names(company_name, filename, partnership_types):
    with open(filename, "r", encoding="utf-8") as f:
        content = f.read()
    parts = content.split("\n\n", 1)
    if len(parts) != 2:
        return {}
    url = parts[0]
    visible_text = parts[1]
    print(f"\nProcessing text of {url}, text length {len(visible_text)}")
    chunks = chunk_text(visible_text, max_length=6000, overlap=500)
    all_partners = {}
    
    partnership_definitions_str = ', '.join([f"{name} defined as {definition}" if definition else name
                                              for name, definition in partnership_types.items()])
    for idx, chunk in enumerate(chunks):
        print(f"Processing chunk {idx+1}/{len(chunks)}")
        prompt = (
            f"Given the following webpage content, extract the names of any partner companies of the company {company_name} "
            "explicitly mentioned on the page. Only list real companies that appear to be manufacturing "
            f"partners, collaborators, or customers of {company_name}. Focus on CAE, CAM, and metrology partnerships. \n\n"
            "If no such partnerships are mentioned, return NOTHING, an empty string. Do NOT make up names or "
            f"guess based on irrelevant information.\n\n"
            f"Only for each valid company found, categorize the partnership into 1 of {len(partnership_types)} categories: "
            f"{partnership_definitions_str}\n\n"
            "For each partner, also classify the partner company into one of these four domains: "
            "'CAE', 'CAM', 'Metrology devices', or 'Metrology software'. Choose the single most relevant domain.\n\n"
            "Return the results in the exact format:\n"
            "Company Name: partnership type | industry domain\n\n"
            "Example:\n"
            "Acme Corp: software partner | CAE\n"
            "Beta Solutions: reseller | Metrology devices\n\n"
            f"Webpage Content:\n{chunk}"
        )
        try:
            response = client.chat.completions.create(
                model="gpt-4-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that extracts company partnerships."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=512,
            )
            result = response.choices[0].message.content.strip()
            print(f"Raw OpenAI response:\n{result}")
            for line in result.split("\n"):
                if ":" in line and "|" in line:
                    name_part, rest = line.split(":", 1)
                    type_part, domain_part = rest.split("|", 1)
                    name = name_part.strip().lower()
                    ptype = type_part.strip()
                    domain = domain_part.strip()
                    if name and name not in {"none", "n/a", company_name.lower()}:
                        all_partners[name] = {
                            "type": ptype,
                            "domain": domain
                        }
        except Exception as e:
            print(f"OpenAI API error for {filename} (chunk {idx+1}): {e}")
    return all_partners




def get_all_names(company_name, partnership_types):
    company_name = company_name.lower()
    company_dir = os.path.join("data", company_name)
    if not os.path.exists(company_dir):
        print(f"No data found for {company_name}.")
        return set()
    all_names = set()
    url_to_partners = {}

    for filename in os.listdir(company_dir):
        if filename.endswith(".txt") and filename not in {"urls.txt", "partners.txt", "partners.json"}:
            filepath = os.path.join(company_dir, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            parts = content.split("\n\n", 1)
            url = parts[0] if parts else f"unknown:{filename}"
            name_to_info = get_names(company_name, filepath, partnership_types)
            url_to_partners[url] = [
                {
                    "name": name,
                    "type": name_to_info[name]["type"],
                    "domain": name_to_info[name]["domain"]
                }
                for name in sorted(name_to_info)
            ]
            all_names.update(name_to_info.keys())
    print(f"\n\n{len(all_names)} partner companies found for {company_name}")

    # Save to partners.txt
    partners_path = os.path.join(company_dir, "partners.txt")
    with open(partners_path, "w", encoding="utf-8") as f:
        for name in sorted(all_names):
            f.write(f"{name}\n")
    print(f"Saved partner names to {partners_path}")

    # Save to partners.json
    json_path = os.path.join(company_dir, "partners.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(url_to_partners, f, indent=2)
    print(f"Saved URL-to-partner mapping to {json_path}")

    partnership_dict = merge_data(url_to_partners, company_dir, company_name)
    return partnership_dict


# def merge_data(url_to_partners, company_dir):
#     partner_index = {}
#     for url, partners in url_to_partners.items():
#         for entry in partners:
#             name = entry["name"].lower()
#             ptype = entry["type"]
#             domain = entry["da"]
#             if name not in partner_index:
#                 partner_index[name] = {
#                     "type_counter": Counter(),
#                     "domain_counter": Counter(),
#                     "urls": set()
#                 }
#             partner_index[name]["type_counter"][ptype] += 1
#             partner_index[name]["domain_counter"][domain] += 1
#             partner_index[name]["urls"].add(url)

#     # resolve conflicts by picking the most common values
#     dedup_data = {}
#     for name, info in partner_index.items():
#         dedup_data[name] = {
#             "type": info["type_counter"].most_common(1)[0][0],
#             "domain": info["domain_counter"].most_common(1)[0][0],
#             "urls": sorted(info["urls"])
#         }

#     data_path = os.path.join(company_dir, "data.json")
#     with open(data_path, "w", encoding="utf-8") as f:
#         json.dump(dedup_data, f, indent=2)
#     print(f"Saved merged partner data to {data_path}")

def merge_data(url_to_partners, company_dir, company_name):
    partner_index = {}
    for url, partners in url_to_partners.items():
        for entry in partners:
            name = entry["name"].lower()
            ptype = entry["type"]
            domain = entry["domain"]
            if name not in partner_index:
                partner_index[name] = {
                    "type_counter": Counter(),
                    "domain_counter": Counter(),
                    "urls": set()
                }
            partner_index[name]["type_counter"][ptype] += 1
            partner_index[name]["domain_counter"][domain] += 1
            partner_index[name]["urls"].add(url)

    # Today's date
    today = datetime.today().strftime("%Y-%m-%d")

    # Final output: list of dicts
    merged_partners = []
    for name, info in partner_index.items():
        merged_partners.append({
            "company_name": company_name,
            "partnership_name": name,
            "partnership_domain": info["domain_counter"].most_common(1)[0][0],
            "partnership_type": info["type_counter"].most_common(1)[0][0],
            "url_scraped_from": sorted(info["urls"])[0],  # or include all if needed
            "date_scraped": today,
        })

    data_path = os.path.join(company_dir, "data.json")
    with open(data_path, "w", encoding="utf-8") as f:
        json.dump(merged_partners, f, indent=2)

    print(f"Saved merged partner data to {data_path}")
    return merged_partners



def clear_html(company_name):
    company_name = company_name.lower()
    company_dir = os.path.join("data", company_name)
    if not os.path.exists(company_dir):
        print(f"No data found for {company_name}.")
        return set()

    deleted_files = set()
    for filename in os.listdir(company_dir):
        if filename.startswith("data_"):
            file_path = os.path.join(company_dir, filename)
            try:
                os.remove(file_path)
                deleted_files.add(filename)
            except Exception as e:
                print(f"Failed to delete {filename}: {e}")

    if deleted_files:
        print(f"Deleted {len(deleted_files)} files:")
        # for f in deleted_files:
        #     print("-", f)
    else:
        print("No html files found to delete.")

    return deleted_files

def check_data_exists(company_name):
    company_name = company_name.lower()
    company_dir = os.path.join(DATA_DIR, company_name)
    if not os.path.exists(company_dir):
        return False
    
    data_dir = os.path.join(company_dir, "partners.json")
    if not os.path.exists(data_dir):
        return False
    return True

def pull_partner_data(company_name):
    # call if  data.json already populated
    company_name = company_name.lower()
    data_dir = os.path.join(DATA_DIR, company_name, "data.json")

    if not os.path.exists(data_dir):
        print("path dont even exist")
        return {"success": False}
    
    with open(data_dir, 'r') as f:
        partnership_data = json.load(f)
        return {
            "success": True,
            "data": partnership_data
        }
