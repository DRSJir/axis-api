import os

from flask import jsonify, request
from functools import wraps
from dotenv import load_dotenv

load_dotenv()
ADMIN_API_KEY = os.getenv("ADMIN_API_KEY")

def validate_schema(required_fields):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            data = request.get_json()
            if not data:
                return jsonify({"error": "cuerpo de petición invalido"})

            missing = [field for field in required_fields if field not in data]
            if missing:
                return jsonify({"error": f"faltan campos {', '.join(missing)}"}), 400

            return f(*args, **kwargs)
        return decorated_function
    return decorator

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        key = request.headers.get('X_API_KEY')

        if not key or key.strip() != ADMIN_API_KEY:
            return jsonify({"error": "no autorizado"}), 401

        return f(*args, **kwargs)
    return decorated
