from flask import Flask, jsonify
from flask_cors import CORS

from app.database import db, configure_database
from app.models import Product
from app.routes import api_bp

app = Flask(__name__)
CORS(app)
configure_database(app)
app.register_blueprint(api_bp, url_prefix='/api')

def seed_database():
    with app.app_context():
        db.create_all()
        if Product.query.count() == 0:
            print("Replobando la base de datos...")
            p1 = Product(name="Destornillador Pentalobe P5", price=15.99, stock=10, material="Acero S2", sku="AX-P5")
            p2 = Product(name="Pinzas de Precisión ESD", price=12.50, stock=5, material="Acero Inoxidable",sku="AX-ESD-1")

            db.session.add_all([p1, p2])
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
