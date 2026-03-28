from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


@app.route('/')
def hello_world():
    return {"mensaje": "Hola mundo!"}

@app.route('/api/status', methods=["GET"])
def check_status():
    return jsonify({
        "status": "online",
        "project": "AXIS Precision Tools API",
        "verison": "1.0"
    }), 200


if __name__ == '__main__':
    app.run(debug=True, port=5000)
