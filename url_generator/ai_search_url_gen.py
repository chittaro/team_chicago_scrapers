import openai
import os
import requests
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")

openai.api_key = OPENAI_API_KEY

# Web search function using Google Search API
def google_search(query, num_results=10):
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "q": query,
        "key": GOOGLE_API_KEY,
        "cx": GOOGLE_CSE_ID,
        "num": num_results
    }

    response = requests.get(url, params=params)
    results = response.json()

    urls = [item["link"] for item in results.get("items", [])]
    return urls

# OpenAI function calling
def get_company_partnership_urls(company_name):
    client = openai.OpenAI()

    functions = [
        {
            "name": "google_search",
            "description": "Search Google for real-time information on a topic.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The search query"},
                    "num_results": {"type": "integer", "description": "Number of results to return"}
                },
                "required": ["query"]
            }
        }
    ]

    messages = [
        {"role": "system", "content": "You are an AI assistant that finds real-time URLs about company partnerships."},
        {"role": "user", "content": f"Find 10 URLs about {company_name}'s partnerships."}
    ]

    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=messages,
        functions=functions,
        function_call={"name": "google_search"},
        max_tokens=400,
        temperature=0.3
    )

    # Extract function arguments
    function_args = response.choices[0].message.function_call.arguments
    search_query = function_args.get("query", f"{company_name} partnerships site:.com")
    
    # Perform Google Search
    urls = google_search(search_query)

    return urls[:10]

company_name = input("Enter the company name: ")
urls = get_company_partnership_urls(company_name)

print(f"\nTop 10 URLs for {company_name} partnerships:")
for idx, url in enumerate(urls, start=1):
    print(f"{idx}. {url}")

if urls:
    output_file = f"{company_name}_ai_urls.txt"
    with open(output_file, "w") as file:
        for url in urls:
            file.write(url + "\n")
    print(f"\nRelevant URLs saved to {output_file}")
else:
    print("No relevant URLs found.")
