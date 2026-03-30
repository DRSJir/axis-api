from flask import Blueprint, jsonify, request
from .services import InventoryService
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
    # Obtener los filtros de la URL: ?category=X&device=Y
    category = request.args.get('category')
    model = request.args.get('model')
    search = request.args.get('q')

    products = InventoryService.get_filtered_catalog(
        category_name=category,
        model_name=model,
        search_query=search
    )
    return jsonify(products), 200

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
