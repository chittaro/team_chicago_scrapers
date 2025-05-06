from flask import Flask, jsonify, request
from flask_cors import CORS

import sys, os
# make higher-level functions accessible
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from url_generator.search_url_gen import get_company_partnership_urls
from name_finder.name_type_domain_finder import get_html, get_names, get_all_names, clear_html, pull_partner_data


app = Flask(__name__)
CORS(app)

@app.route('/api/get_urls/<company>/', methods=['GET'])
def get_competitor_urls(company):
    urls = get_company_partnership_urls(company)
    return jsonify({"urls": urls})

@app.route('/api/process_html/<company>/', methods=['GET'])
def process_html(company):
    # TODO: clear & process URLs once more (should be called in sequence w/ get_partner_data on frontend)
    return jsonify({"success": True})

@app.route('/api/get_partner_data/<company>/', methods=['GET'])
def get_partner_data(company):
    # simply pull partnership data from data.json (success: False if doesn't exist)
    # TODO: update code to parse urls/HTML if data.json doesn't exist 
    return jsonify(**pull_partner_data(company)), 201

if __name__ == '__main__':
    app.run(debug=True)
