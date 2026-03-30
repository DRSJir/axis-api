from crypt import methods

from flask import Blueprint, jsonify, request
from sqlalchemy import result_tuple

from .services import InventoryService, CartService
from .validators import validate_schema, admin_required

# Crear un blueprint
api_bp = Blueprint('api', __name__)


@api_bp.route("/checkout", methods=['POST'])
@validate_schema(['product_id', 'quantity'])
def checkout():
    data = request.get_json()
    result = InventoryService.process_purchase(
        data['product_id'],
        data['quantity']
    )

    status = result.pop('status')
    return jsonify(result), status

@api_bp.route('/status', methods=["GET"])
def check_status():
    return jsonify({
        "status": "online",
        "project": "AXIS Precision Tools API",
        "verison": "1.0"
    }), 200

@api_bp.route('/products', methods=['GET'])
def get_products():
    # Parámetros de paginación
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 8, type=int)

    # Obtener los filtros de la URL: ?category=X&device=Y
    category = request.args.get('category')
    model = request.args.get('model')
    query = request.args.get('q')

    result = InventoryService.get_paginated_catalog(
        page=page,
        per_page=per_page,
        category_name=category,
        model_name=model,
        search_query=query
    )
    return jsonify(result), 200

@api_bp.route("/product/<int:id>", methods=['GET'])
def get_product(id):
    product = InventoryService.get_product_by_id(id)
    return jsonify(product), 200

@api_bp.route("/products", methods=['POST'])
@admin_required
@validate_schema(['name', 'price', 'sku', 'stock', 'category'])
def add_product():
    data = request.get_json()
    result = InventoryService.create_product(data)

    status = result.pop('status', 400)
    return jsonify(result), status

@api_bp.route("/products/<int:id>", methods=["PUT"])
@admin_required
def update_stock(id):
    data = request.get_json()

    if not data or 'stock' not in data:
        return jsonify({"error": "falta campo stock"}), 400

    product = InventoryService.update_product_stock(id, data['stock'])

    if not product:
        return jsonify({"error": "producto no encontrado"})

    return jsonify(product), 200




@api_bp.route("/cart", methods=['GET'])
def summary():
    # Resumen con subtotales e impuestos
    summary = CartService.get_cart_summary()
    return jsonify(summary), 200

@api_bp.route("/cart", methods=['POST'])
@validate_schema(['product_id', 'quantity'])
def add_to_cart():
    data = request.get_json()
    result = CartService.add_to_cart(data['product_id'], data['quantity'])
    status = result.pop('status', 200)
    return jsonify(result), status

@api_bp.route("/cart/checkout", methods=['POST'])
def checkout_order():
    # Validar token de pago stripe, paypal...
    result = CartService.complete_checkout()

    if result is None:
        return jsonify({"error": "Error interno: el servicio no devolvió respuesta"}), 500

    status = result.pop('status', 200)
    return jsonify(result), status
