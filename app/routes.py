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


@api_bp.route('/cart', methods=['GET'])
def get_cart_summary():
    # buscamos el ID en los Headers de la petición
    session_id = request.headers.get('X-Session-ID') or request.args.get('X-Session-ID')

    # si no viene en el Header, podemos buscarlo en los parámetros de la URL como respaldo
    if not session_id:
        return jsonify({"error": "No se detectó X-Session-ID en Headers ni en Query Params"}), 400

    if not session_id:
        return jsonify({"error": "Se requiere X-Session-ID para ver el carrito"}), 400

    # AHORA SÍ: Pasamos el session_id al servicio
    summary = CartService.get_cart_summary(session_id)
    return jsonify(summary), 200


@api_bp.route("/cart", methods=['POST'])
@validate_schema(['product_id', 'quantity'])
def add_to_cart():
    data = request.get_json()

    # extraer el session_id del header
    session_id = request.headers.get('X-Session-ID')

    # validar que el session_id exista
    if not session_id:
        return jsonify({"error": "Falta el header X-Session-ID"}), 400

    # pasar el session_id a la función del servicio
    user_id = getattr(request, 'user_id', None)

    result = CartService.add_to_cart(
        product_id=data['product_id'],
        quantity=data['quantity'],
        session_id=session_id,
        user_id=user_id
    )

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
