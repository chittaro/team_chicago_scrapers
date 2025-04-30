from flask import Flask, jsonify, request
from flask_cors import CORS

import sys, os
# make higher-level functions accessible
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from url_generator.search_url_gen import get_company_partnership_urls
from name_finder.name_type_finder import get_html, get_names, get_all_names, clear_html


app = Flask(__name__)
CORS(app)

@app.route('/', methods=['GET'])
def home_route():
    return jsonify({"status": "yass"})


@app.route('/api/get_urls/<company>/', methods=['GET'])
def get_competitor_urls(company):
    urls = get_company_partnership_urls(company)
    return jsonify({"urls": urls})

'''
TODO: change URL-->HTML to only read files that are left over from UI (ignore Xed out files)
'''
@app.route('/api/process_urls/<company>/', methods=['GET'])
def fetch_competitor_urls(company):
    clear_html(company)
    get_html(company)
    return jsonify({"success": True})

@app.route('/api/get_partner_data/<company>/', methods=['GET'])
def get_partner_data(company):
    data = {
        "row": {
            "partner_name": "PARTNER A",
            "url_sources": ["www.test.com", "www.test2.com"]
        }
    }

    return jsonify(**data), 201

if __name__ == '__main__':
    app.run(debug=True)
