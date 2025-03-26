import os
import time
import sys
from urllib.parse import quote
import concurrent
import uuid
import openai
import re
from bs4 import BeautifulSoup
from dotenv import load_dotenv

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(parent_dir)
from scraper_helper import fetch_page

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
    filename = os.path.join(folder_path, f"{unique_id}.txt")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"{url}\n\n{text}")
    print(f"Saved: {filename}")


def get_html(company_name, urls):
    def process(url):
        html = fetch_page(url)
        if html:
            soup = BeautifulSoup(html, "html.parser")
            text = soup.get_text(separator="\n", strip=True)
            write_text_to_file(company_name, url, text)
            return 1
        else:
            print(f"Failed: {url}")
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
    return chunks


def get_names(filename):
    with open(filename, "r", encoding="utf-8") as f:
        content = f.read()

    parts = content.split("\n\n", 1)
    if len(parts) != 2:
        return set()
    url = parts[0]
    visible_text = parts[1]

    print(f"Processing text of {url}, text length {len(visible_text)}")

    chunks = chunk_text(visible_text, max_length=6000, overlap=500)
    all_names = set()

    for idx, chunk in enumerate(chunks):
        print(f"Processing chunk {idx+1}/{len(chunks)}")
        prompt = (
            "Given the following webpage content, extract the names of any partner companies "
            "explicitly mentioned on the page. Only list companies that appear to be business "
            "partners, collaborators, or customers of the main company behind this website.\n\n"
            "If no such partnerships are mentioned, return nothing. Do NOT make up names or "
            "guess based on irrelevant information. Do not include the main company name itself.\n\n"
            "Extracted partner company names should be returned as a comma-separated list, no duplicates.\n\n"
            f"Webpage Content:\n{chunk}"
        )

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


# Example usage
# ex_filename = '6db48ba3-2eca-46b8-ba5d-510a187e4877.txt'
ex_filename = '16838a97-f8f9-42b4-9502-6c9b89ed679a.txt'
names = get_names(ex_filename)
print(f"Names: {names}")
