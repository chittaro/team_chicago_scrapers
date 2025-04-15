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
    return sheet_names

def get_competitor_data(sheet_name):
    sheet_range = f"'{sheet_name}'!A1:Z100"

    url = f'https://sheets.googleapis.com/v4/spreadsheets/{SHEET_ID}/values/{sheet_range}?key={API_KEY}'
    response = requests.get(url)
    data = response.json()

    values = data.get('values', [])
    if len(values) > 0:
        headers = values[0]
    else:
        return None

    rows = values[1:]

    # reduce data to relevant columns
    filt_headers = []
    filt_rows = []
    filt_indices = []
    relevant_headers = ["Partner Name", "Partnership Type", "Links"]
    pattern = "|".join(relevant_headers)
    for idx, h in enumerate(headers):
        match = re.search(pattern, h, re.IGNORECASE)
        if match:
            filt_headers.append(match.group())
            filt_indices.append(idx)

    filt_rows = [[row[i] if i < len(row) else None for i in filt_indices] for row in rows]
    df = pd.DataFrame(filt_rows, columns=filt_headers)

    # reduce df to relevant headers
    # relevant_indices = []
    # for i, s in enumerate(headers):
    #     for h in relevant_headers:
    #         if re.search(f'{h}', s, re.IGNORECASE):
    #             relevant_indices.append(i)
    #             df.rename(columns={s: h}, inplace=True)

    if df.empty:
        return None

    print(f"\n\n********** Fetched data from competitor: {sheet_name}")
    print(f"\nSample of data: ")
    print(df.head(2))

    return df

def write_competitor_data():
    competitors = get_document_tabs()

    data_dir = os.path.join(parent_dir, "manual_data")
    os.makedirs(data_dir, exist_ok=True)
    
    for c in competitors:
        # normalize competitor name
        normed_name = '_'.join(c.lower().split(' '))

        print(f"\n\n********** Getting data from competitor: {c}")
        competitor_df = get_competitor_data(c)
        if competitor_df is not None:
            # create/overwrite competitor csv with google sheet data
            data_path = os.path.join(data_dir, f"{normed_name}_data.csv")
            print(f"\n\n********** Writing {c}'s data to path: {data_path}")
            competitor_df.to_csv(data_path, index=False)
        else:
            print(f"NONE FOUND -- skipping competitor {c}")
