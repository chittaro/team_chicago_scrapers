from urllib.parse import urlparse
import openai
import re
import os
from dotenv import load_dotenv

# openai.api_key = os.getenv("OPENAI_API_KEY")
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("Add your OpenAI key to your .env file.")
openai.api_key = api_key

######################
# Option 1 blacklist #
######################

def is_relevant_url(url):
    # lily version, ask Fabrizio if we care about reseller partners
    blacklist_keywords = ['careers', 'jobs', 'contact', 'privacy', 'blog', 'login', 'forum']
    domain_blacklist = ['linkedin.com', 'facebook.com', 'twitter.com', 'reddit.com']

    parsed = urlparse(url)
    domain = parsed.netloc.lower()

    if any(domain in d for d in domain_blacklist):
        return False
    if any(k in url.lower() for k in blacklist_keywords):
        return False
    if not parsed.scheme.startswith("http"):
        return False
    return True

######################
# Option 2 ranking #
######################
def score_url(url, company_name):
    score = 0
    lowered_url = url.lower()
    
    # Add weight for partnership-related terms
    if 'partner' in lowered_url or 'alliance' in lowered_url:
        score += 0.5

    # Add weight if company name is in the URL
    if company_name.lower() in lowered_url:
        score += 0.2

    # Reward certain domains
    if url.endswith(".com") and not any(s in lowered_url for s in ['linkedin', 'facebook', 'twitter']):
        score += 0.2

    # Penalize pages like contact/legal/careers
    if any(k in lowered_url for k in ['careers', 'jobs', 'contact', 'about', 'privacy', 'terms']):
        score -= 0.3

    # Bonus for reputable domains
    trusted_sources = ['businesswire.com', 'reuters.com', 'bloomberg.com']
    if any(source in lowered_url for source in trusted_sources):
        score += 0.3

    return score

# def get_company_partnership_urls(company_name):
#     client = openai.OpenAI()
    
#     # prompt = f"Search for 10 URLs that contain relevant information about {company_name}'s partner companies and the nature of their partnership. Return a list of only these URLs."
#     prompt = f"List 10 URLs that contain information about {company_name}'s partner companies and the nature of their partnerships. Return only valid URLs, with no extra text, descriptions, or explanations."
    
#     response = client.chat.completions.create(
#          # model="gpt-4o-mini",
#         model="gpt-4-turbo",
#         messages=[
#             {"role": "system", "content": "You are an AI assistant that finds only valid URLs related to company partnerships."},
#             {"role": "user", "content": prompt}
#         ],
#         max_tokens=400,
#         temperature=0.3  # lower for more deterministic results
#     )

#     response_text = response.choices[0].message.content.strip()
#     print(response_text)

#     # url_pattern = r'https?://[^\s)]+'
#     # url_pattern = r'\((https?://[^\s)]+)\)'  # Captures URLs inside parentheses
#     url_pattern = r'https?://[^\s\)]+'
#     urls = re.findall(url_pattern, response_text)
#     unique_urls = list(set(urls))

#     #apply filtration here
#     filtered_urls = [url for url in unique_urls if is_relevant_url(url)]
#     ## option 2
#     # scored_urls = [(url, score_url(url, company_name)) for url in unique_urls]]
#     # scored_urls.sort(key = lambda x: x[1], reverse = true) # sort by score, decending
#     # top_urls = [url for url, score in scored_urls if score > 0][:10] # optional threshold

#     #return filtered_urls[:10]

#     return list(set(urls))[:10]  # remove duplicates and limit to 10


# company_name = input("Enter the company name: ")
# urls = get_company_partnership_urls(company_name)
# print(f"\nTop 10 relevant URLs for {company_name} partnerships:\n{urls}")
# if urls:
#     output_file=f"{company_name}_urls.txt"
#     with open(output_file, "w") as file:
#         for url in urls:
#             file.write(url + "\n")
#     print(f"\nRelevant URLs saved to {output_file}")
# else:
#     print("No relevant URLs found.")

