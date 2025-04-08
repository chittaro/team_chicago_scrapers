import openai
import re
import os
from dotenv import load_dotenv


parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
env_path = os.path.join(parent_dir, ".env")
load_dotenv(dotenv_path=env_path)
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("Add your OpenAI key to your .env file.")
openai.api_key = api_key


def get_company_partnership_urls(company_name):
    client = openai.OpenAI()
    
    # prompt = f"Search for 10 URLs that contain relevant information about {company_name}'s partner companies and the nature of their partnership. Return a list of only these URLs."
    prompt = f"List 10 URLs that contain information about {company_name}'s partner companies and the nature of their partnerships. Return only valid URLs, with no extra text, descriptions, or explanations."
    
    response = client.chat.completions.create(
         # model="gpt-4o-mini",
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": "You are an AI assistant that finds only valid URLs related to company partnerships."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=400,
        temperature=0.3  # lower for more deterministic results
    )

    response_text = response.choices[0].message.content.strip()
    print(response_text)

    # url_pattern = r'https?://[^\s)]+'
    # url_pattern = r'\((https?://[^\s)]+)\)'  # Captures URLs inside parentheses
    url_pattern = r'https?://[^\s\)]+'
    urls = re.findall(url_pattern, response_text)

    return list(set(urls))[:10]  # remove duplicates and limit to 10


company_name = input("Enter the company name: ")
urls = get_company_partnership_urls(company_name)
print(f"\nTop 10 relevant URLs for {company_name} partnerships:\n{urls}")
if urls:
    output_file=f"{company_name}_urls.txt"
    with open(output_file, "w") as file:
        for url in urls:
            file.write(url + "\n")
    print(f"\nRelevant URLs saved to {output_file}")
else:
    print("No relevant URLs found.")
