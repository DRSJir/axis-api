from flask import Blueprint, jsonify, request, abort
from .database import db
from .models import Product

# Crear un blueprint
api_bp = Blueprint('api', __name__)

# Simular usuarios
ADMIN_API_KEY = "axis_secret_2026"

def checkout():
    key = request.headers.get('X-API-KEY')
    if key != ADMIN_API_KEY:
        abort(401, description="No autorizado: API Key inválida o ausente")

@api_bp.route('/status', methods=["GET"])
def check_status():
    return jsonify({
        "status": "online",
        "project": "AXIS Precision Tools API",
        "verison": "1.0"
    }), 200

@api_bp.route('/products', methods=['GET'])
def get_products():
    products = Product.query.all()
    return jsonify([p.to_dict() for p in products])

@api_bp.route("/product/<int:id>", methods=['GET'])
def get_product(id):
    produc = Product.query.get_or_404(id)
    return jsonify(produc.to_dict()), 200

@api_bp.route("/products", methods=['POST'])
def add_product():
    checkout()
    data = request.get_json()

    new_product = Product(
        name = data["name"],
        price = data["price"],
        stock = data["stock"],
        material = data.get("material"),
        sku = data["sku"]
    )
    db.session.add(new_product)
    db.session.commit()

    return jsonify(new_product.to_dict()), 201

@api_bp.route("/products/<int:id>", methods=["PUT"])
def update_stock(id):
    checkout()
    product = Product.query.get_or_404(id)
    data = request.get_json()

    if 'stock'in data:
        product.stock = data["stock"]

    db.session.commit()
    return jsonify(product.to_dict()), 201
