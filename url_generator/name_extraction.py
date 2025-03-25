import os
import openai
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
INPUT_FILE = "raw_html_test.txt"
if not api_key:
    raise ValueError("Add your OpenAI key to your .env file.")
openai.api_key = api_key

def get_company_name(text: str):
    client = openai.OpenAI()
    
    # prompt = f"Search for 10 URLs that contain relevant information about {company_name}'s partner companies and the nature of their partnership. Return a list of only these URLs."
    prompt = f"""Return the names of the two companies forming a partnership as discussed in this text: {text}.
    Return only the company names, separated by commas, with no extra text, descriptions, or explanations.
    If the text does not in any way describe a partnership between two companies, output 'ERROR: No partnership found'."""
    
    response = client.chat.completions.create(
         # model="gpt-4o-mini",
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are an AI assistant that only identfies two core company names being discussed in a given text."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=400,
        temperature=0.3  # lower for more deterministic results
    )

    response_text = response.choices[0].message.content.strip()
    print(response_text)

with open(INPUT_FILE) as file:
    file_text = " ".join(file.readlines())
    print(file_text)
    get_company_name(file_text)
