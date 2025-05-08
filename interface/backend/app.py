import json
from flask import Flask, jsonify, request
from flask_cors import CORS

import sys, os, time
# make higher-level functions accessible
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from url_generator.search_url_gen import get_company_partnership_urls
from name_finder.name_type_domain_finder import get_html, get_names, get_all_names, clear_html, pull_partner_data

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DATA_ROOT = os.path.join(REPO_ROOT, "data")

app = Flask(__name__)
CORS(app)

@app.route('/api/get_urls/<company>/', methods=['GET'])
def get_competitor_urls(company):
    ''' Fetches & returns list of relevant company URLs '''
    urls = get_company_partnership_urls(company)
    return jsonify({"urls": urls})

@app.route('/api/process_html/<company>/', methods=['GET'])
def process_html(company):
    ''' Deletes and updates HTML with most recent urls.txt file
        Returns json dictionary of complete partnership data '''
    clear_html(company)
    get_html(company)
    partnerships = get_all_names
    if len(partnerships) == 0:
        data = {
            "success": False,
            "data": {}
        }

    else: 
        data = {
            "success": True,
            "data": partnerships
        }

    return jsonify(**data)

@app.route('/api/get_partner_data/<company>/', methods=['GET'])
def get_partner_data(company):
    ''' Returns json dictionary of complete partnership data '''
    return jsonify(**pull_partner_data(company)), 201



# -- TEST ROUTES -- #
# used to avoid expending tokens during application testing

@app.route('/api/test/get_urls/<company>/', methods=['GET'])
def test_get_competitor_urls(company):
    time.sleep(2)
    return jsonify({
        "urls": [
            "https://www.autodesk.com/",
            "https://aps.autodesk.com/certified-partners-list",
            "https://brand.autodesk.com/co-branding/"
        ]}
    ), 201


@app.route('/api/test/process_html/<company>/', methods=['GET'])
def test_process_html(company):
    time.sleep(5)
    return jsonify({
        "success": True,
        "data": {
            "datum360": {
                "type": "strategic partner",
                "domain": "CAE",
                "urls": [
                "https://aecpartners.autodesk.com/?lang=en"
                ]
            },
            "eptura": {
                "type": "strategic partner",
                "domain": "Metrology software",
                "urls": [
                "https://adsknews.autodesk.com/en/views/embracing-aeco/",
                "https://aecpartners.autodesk.com/?lang=en",
                "https://intandem.autodesk.com/resource/eptura/",
                "https://www.autodesk.com/partners/strategic-alliance-partners"
                ]
            },
        }
    }), 201

@app.route('/api/test/get_partner_data/<company>/', methods=['GET'])
def test_get_partner_data(company):
    time.sleep(1)
    return jsonify({
        "success": True,
        "data": {
            "datum360": {
                "type": "strategic partner",
                "domain": "CAE",
                "urls": [
                "https://aecpartners.autodesk.com/?lang=en"
                ]
            },
            "eptura": {
                "type": "strategic partner",
                "domain": "Metrology software",
                "urls": [
                "https://adsknews.autodesk.com/en/views/embracing-aeco/",
                "https://aecpartners.autodesk.com/?lang=en",
                "https://intandem.autodesk.com/resource/eptura/",
                "https://www.autodesk.com/partners/strategic-alliance-partners"
                ]
            },
        }
    }), 201


if __name__ == '__main__':
    app.run(debug=True)
