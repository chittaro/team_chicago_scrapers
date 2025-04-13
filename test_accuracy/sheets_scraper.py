import requests
import re
import os
import sys
import pandas as pd
from dotenv import load_dotenv


parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(parent_dir)
env_path = os.path.join(parent_dir, ".env")
load_dotenv(dotenv_path=env_path)
API_KEY = os.getenv("SHEETS_API_KEY")

SHEET_ID = "1NkwnH4A4ICCr_afqPhwJ2ry_-URsLzOlOkcajMMIaeM"

def get_document_tabs():
    url = f'https://sheets.googleapis.com/v4/spreadsheets/{SHEET_ID}?key={API_KEY}'
    response = requests.get(url)
    data = response.json()

    # Extract sheet/tab names
    sheet_names = [sheet['properties']['title'] for sheet in data['sheets']]
    sheet_names.remove('Players')
    sheet_names.remove('PB_CACHE')
    return sheet_names

def get_competitor_data(sheet_name):
    sheet_range = f"'{sheet_name}'!A1:Z100"

    url = f'https://sheets.googleapis.com/v4/spreadsheets/{SHEET_ID}/values/{sheet_range}?key={API_KEY}'
    response = requests.get(url)
    data = response.json()

    print(f"********** Getting data from competitor: {sheet_name}")
    values = data.get('values', [])
    headers = values[0]
    rows = values[1:]

    df = pd.DataFrame(rows, columns=headers)

    # reduce df to relevant headers
    relevant_headers = ["Partner Name", "Partnership Type", "Links"]
    relevant_indices = []
    for i, s in enumerate(headers):
        for h in relevant_headers:
            if re.search(f'{h}', s, re.IGNORECASE):
                relevant_indices.append(i)
                df.rename(columns={s: h}, inplace=True)

    df_filt = df.iloc[:, relevant_indices]

    return df_filt

def get_all_competitor_data():
    competitors = get_document_tabs()
    test_df = get_competitor_data(competitors[0])
    print(test_df.head(2))