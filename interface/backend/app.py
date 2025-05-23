import json
from flask import Flask, jsonify, request
from flask_cors import CORS

import sys, os, time
# make higher-level functions accessible
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from url_generator.search_url_gen import get_company_partnership_urls
from name_finder.name_type_domain_finder import get_html, get_names, get_all_names, clear_html, pull_partner_data
from interface.backend.db_operations import (
    get_partnership_type_defs,
    fetch_all_partnership_data
)
# Import the settings blueprint using absolute-like path from project root
from interface.backend.routes_settings import settings_bp

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DATA_ROOT = os.path.join(REPO_ROOT, "data")

app = Flask(__name__)
CORS(app)

# Register the settings blueprint
# All routes in settings_bp will be prefixed with /api (from settings_bp) further prefixed by this /api if needed,
# but settings_bp already has /api/settings, so it will be /api/settings
app.register_blueprint(settings_bp) 

@app.route('/api/get_urls/<company>/', methods=['GET'])
def get_competitor_urls(company):
    ''' Fetches & returns list of relevant company URLs '''
    urls = get_company_partnership_urls(company)
    return jsonify({"urls": urls})

@app.route('/api/process_data/<company>/', methods=['GET'])
def process_data(company):
    ''' Deletes and updates HTML with most recent urls.txt file, queries LLM for classification
        Returns json dictionary of complete partnership data '''
    partnership_types = get_partnership_type_defs()
    if partnership_types is None:
        return jsonify(success=False, data={})

    clear_html(company)
    get_html(company)
    partnerships = get_all_names(company, partnership_types)
    print(f"API response: {partnerships}")
    if not partnerships:
        return jsonify(success=False, data={})

    return jsonify(success=True, data=partnerships)

@app.route('/api/get_partner_data/<company>/', methods=['GET'])
def get_partner_data(company):
    ''' Returns json dictionary of partnership data for single company '''
    return jsonify(**pull_partner_data(company)), 201

@app.route('/api/get_all_partner_data/', methods=['GET'])
def get_all_partner_data():
    ''' Returns json dictionary of partnership data for single company '''
    return jsonify(success=True, data=fetch_all_partnership_data()), 201


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


@app.route('/api/test/process_data/<company>/', methods=['GET'])
def test_process_data(company):
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


@app.route('/api/test/get_all_partner_data/', methods=['GET'])
def test_get_all_partner_data():
    ''' Returns json dictionary of partnership data for single company '''
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
