from flask import Flask, jsonify
from flask_cors import CORS

from app.database import db, configure_database
from app.models import Product, Category, Device
from app.routes import api_bp

app = Flask(__name__)
CORS(app)
configure_database(app)
app.register_blueprint(api_bp, url_prefix='/api')


def seed_database():
    with app.app_context():
        db.drop_all()
        db.create_all()

        # --- 1. Definir Categorías ---
        herramientas = Category(name="herramientas")
        refacciones = Category(name="refacciones")
        kits = Category(name="kits")

        # --- 2. Definir Dispositivos ---
        ip13 = Device(model_name="iPhone 13")
        ip15 = Device(model_name="iPhone 15")
        s22 = Device(model_name="Samsung S22")
        pixel8 = Device(model_name="Google Pixel 8")

        # --- 3. Crear Productos con Relaciones Cruzadas ---

        # Producto 1: Solo para iPhone 13 (Herramienta)
        p1 = Product(name="Destornillador P5", price=12.5, stock=50, sku="AX-P5", category=herramientas)
        p1.compatible_devices.extend([ip13])

        # Producto 2: Para todos los iPhones (Herramienta)
        p2 = Product(name="Espátula iSesamo", price=8.0, stock=100, sku="AX-ISE", category=herramientas)
        p2.compatible_devices.extend([ip13, ip15])

        # Producto 3: Refacción específica para Samsung (Refacción)
        p3 = Product(name="Puerto de Carga S22", price=25.0, stock=10, sku="AX-CH-S22", category=refacciones)
        p3.compatible_devices.extend([s22])

        # Producto 4: Kit Universal (Kit)
        p4 = Product(name="Kit Essential AXIS", price=45.0, stock=20, sku="AX-K-ESS", category=kits)
        p4.compatible_devices.extend([ip13, ip15, s22, pixel8])

        db.session.add_all([herramientas, refacciones, kits, ip13, ip15, s22, pixel8, p1, p2, p3, p4])
        db.session.commit()
        print("Base de datos lista")

seed_database()

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Recurso no encontrado", "code": 404}), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({"error": "Error interno del servidor", "code": 500}), 500

@app.errorhandler(401)
def unauthorized(error):
    return jsonify({"error": "No autorizado", "code": 401}), 401

if __name__ == '__main__':
    app.run(debug=True, port=5000)
