import json
from flask import Flask, jsonify, request
from flask_cors import CORS

import sys, os
# make higher-level functions accessible
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from url_generator.search_url_gen import get_company_partnership_urls
from name_finder.name_type_finder import get_html, get_names, get_all_names, clear_html

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DATA_ROOT = os.path.join(REPO_ROOT, "data")

app = Flask(__name__)
CORS(app)

@app.route('/', methods=['GET'])
def home_route():
    return jsonify({"status": "yass"})


@app.route('/api/get_urls/<company>/', methods=['GET'])
def get_competitor_urls(company):
    # urls = get_company_partnership_urls(company)
    urls_file = os.path.join(DATA_ROOT, company, "urls.txt")
    with open(urls_file, "r") as f:
        urls = [line.strip() for line in f if line.strip()]

    return jsonify({"urls": urls})

'''
TODO: change URL-->HTML to only read files that are left over from UI (ignore Xed out files)
'''
# @app.route('/api/process_urls/<company>/', methods=['GET'])
# def fetch_competitor_urls(company):
#     # clear_html(company)
#     # get_html(company)
#     return jsonify({"success": True})

@app.route('/api/get_partner_data/<company>/', methods=['GET'])
def get_partner_data(company):
    data_path = os.path.join(DATA_ROOT, company, "data.json")
    if not os.path.exists(data_path):
        return jsonify({"error": f"No data.json found for {company}"}), 404

    with open(data_path, "r", encoding="utf-8") as f:
        partner_data = json.load(f)
    # print(partner_data)
    return jsonify({"partners": partner_data})


    # data = {
    #     "row": {
    #         "partner_name": "PARTNER A",
    #         "url_sources": ["www.test.com", "www.test2.com"]
    #     }
    # }

    return jsonify(**data), 201

if __name__ == '__main__':
    app.run(debug=True)
