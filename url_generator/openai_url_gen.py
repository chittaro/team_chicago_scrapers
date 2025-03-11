import openai
import re
import requests

def get_company_partnership_urls(company_name):
    openai.api_key = 'TODO-openai-api-key'

    prompt = f"Search for 10 URLs that contain relevant information about {company_name}'s partner companies and the nature of their partnership. Return a list of only these URLs."

    response = openai.Completion.create(
        # model="text-davinci-003",
        model="gpt-4-turbo",
        prompt=prompt,
        max_tokens=150,  # limit number of tokens in the response
        n=1,
        stop=None,
        temperature=0.7
    )
    
    response_text = response["choices"][0]["text"].strip()

    # regex to extract URLs
    url_pattern = r'https?://[^\s)]+'
    urls = re.findall(url_pattern, response_text)

    return urls[:10]


company_name = input("Enter the company name: ")
urls = get_company_partnership_urls(company_name)
print(f"Top 10 relevant URLs for {company_name} partnerships:\n{urls}")
