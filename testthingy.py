import os
import requests
from dotenv import load_dotenv

load_dotenv()

# Get API key and search engine ID from environment variables
api_key = os.getenv("GOOGLE_API_KEY")
search_engine_id = os.getenv("GOOGLE_SEARCH_ENGINE_ID")

print(f"API Key (first 5 chars): {api_key[:5]}...") # Shows just beginning for security
print(f"Search Engine ID: {search_engine_id}")

# Test the API with a simple query
def test_google_api():
    query = "test"
    url = f"https://www.googleapis.com/customsearch/v1"
    params = {
        "key": api_key,
        "cx": search_engine_id,
        "q": query
    }
    
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            print(f"API call successful! Found {len(data.get('items', []))} results.")
            return True
        else:
            print(f"API call failed with status code: {response.status_code}")
            print(f"Error message: {response.text}")
            return False
    except Exception as e:
        print(f"Exception occurred: {e}")
        return False

test_google_api()