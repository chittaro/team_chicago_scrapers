# backend/app.py
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/', methods=['GET'])
def get_competitors():
    return jsonify({"status": "yass"})

if __name__ == '__main__':
    app.run(debug=True)
