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

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(parent_dir)
from scraper_helper import fetch_page, fetch_page_selenium

env_path = os.path.join(parent_dir, ".env")
load_dotenv(dotenv_path=env_path)
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("Add your OpenAI key to your .env file.")

client = openai.OpenAI(api_key=api_key)



def write_text_to_file(company_name, url, text):
    folder_path = os.path.join("data", company_name)
    os.makedirs(folder_path, exist_ok=True)
    unique_id = str(uuid.uuid4())
    filename = os.path.join(folder_path, f"data_{unique_id}.txt")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"{url}\n\n{text}")
    print(f"Saved: {filename}")

# def write_text_to_file(company_name, url, text):
#     folder_path = os.path.join("data", company_name)
#     os.makedirs(folder_path, exist_ok=True)
#     # Sanitize and hash the URL for filename
#     parsed = urlparse(url)
#     clean_name = parsed.netloc + parsed.path.replace('/', '_').strip('_')
#     if not clean_name:
#         clean_name = "homepage"
#     # In case the filename is still too long or not unique, add a hash
#     url_hash = hashlib.sha256(url.encode()).hexdigest()[:8]
#     filename = f"{clean_name}_{url_hash}.txt"
#     filepath = os.path.join(folder_path, filename)
#     with open(filepath, "w", encoding="utf-8") as f:
#         f.write(f"{url}\n\n{text}")
#     print(f"Saved: {filepath}")

def get_html(company_name):
    # load urls from file (already filtered)
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
        else:
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


def get_names(company_name, filename):
    with open(filename, "r", encoding="utf-8") as f:
        content = f.read()

    parts = content.split("\n\n", 1)
    if len(parts) != 2:
        return set()
    url = parts[0]
    visible_text = parts[1]

    print(f"\nProcessing text of {url}, text length {len(visible_text)}")

    chunks = chunk_text(visible_text, max_length=6000, overlap=500)
    all_names = set()

    for idx, chunk in enumerate(chunks):
        print(f"Processing chunk {idx+1}/{len(chunks)}")
        prompt = (
            f"Given the following webpage content, extract the names of any partner companies of the company {company_name} "
            "explicitly mentioned on the page. Only list real companies that appear to be manufacturing "
            f"partners, collaborators, or customers of {company_name}. Focus on CAE, CAM, and metrology partnerships. \n\n"
            "If no such partnerships are mentioned, return nothing, an empty string. Do NOT make up names or "
            f"guess based on irrelevant information. Do not include {company_name} itself.\n\n"
            "Extracted partner company names should be returned as a comma-separated list, no duplicates.\n\n"
            f"Webpage Content:\n{chunk}"
        ) # TODO: only look at partnerships for their manufacturing work (CAE CAM and metrology)

        try:
            response = client.chat.completions.create(
                model="gpt-4-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that extracts company names."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=256,
            )

            result = response.choices[0].message.content.strip().lower()
            print(f"Raw OpenAI response: {result}")

            if any(bad in result for bad in ["no partner", "no relevant", "none", "n/a"]):
                continue

            names = [name.strip() for name in re.split(r',|\n', result) if name.strip()]
            names = [name for name in names if name not in {
                "none", "n/a", "no partners", "partner companies: none"
            }]
            all_names.update(name.lower() for name in names)

        except Exception as e:
            print(f"OpenAI API error for {filename} (chunk {idx+1}): {e}")

    return all_names


def get_all_names(company_name):
    # for all files in the correct company dir other than urls.txt partners.txt, call get_names(filename)
    company_dir = os.path.join("data", company_name)
    if not os.path.exists(company_dir):
        print(f"No data found for {company_name}.")
        return set()

    all_names = set()
    url_to_names = {}

    for filename in os.listdir(company_dir):
        if filename.startswith("data_"):
            filepath = os.path.join(company_dir, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            parts = content.split("\n\n", 1)
            url = parts[0] if parts else f"unknown:{filename}"

            names = get_names(company_name, filepath)
            url_to_names[url] = sorted(names)
            all_names.update(names)


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
        json.dump(url_to_names, f, indent=2)
    print(f"Saved URL-to-partner mapping to {json_path}")

    return all_names


def clear_html(company_name):
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

# Example usage
# ex_filename = '16838a97-f8f9-42b4-9502-6c9b89ed679a.txt'
# names = get_names("autodesk", ex_filename)
# print(f"Names: {names}")
