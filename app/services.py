from itertools import product

from app.database import db
from app.models import Product

class InventoryService:
    @staticmethod
    def process_purchase(product_id, quantity):
        product = Product.query.get(product_id)

        if not product:
            return {"error": "producto no encontrado", "status": 404}

        if product.stock < quantity:
            return {
                "error": "stock insufuciente",
                "available": product.stock,
                "status": 400
            }

        try:
            product.stock -= quantity
            db.session.commit()
            return {
                "mensaje": "compra exitosa",
                "product": product.name,
                "new stock": product.stock,
                "status": 200
            }

        except Exception:
            db.session.rollback()
            return {"error": "error de la base de datos", "status": 500}

    @staticmethod
    def create_product(data):
        try:
            new_prod = Product(
                name=data["name"],
                price=data["price"],
                stock=data["stock"],
                sku=data["sku"],
                material=data.get('material')
            )

            db.session.add(new_prod)
            db.session.commit()
            return new_prod.to_dict()

        except Exception:
            db.session.rollback()
            None

    @staticmethod
    def get_all_products():
        products = Product.query.all()
        return [product.to_dict() for product in products]

    @staticmethod
    def get_product_by_id(id):
        product = Product.get(id)
        return product.to_dict() if product else None

    @staticmethod
    def update_product_stock(id, new_stock):
        product = Product.query.get(id)
        if product:
            product.stock = new_stock
            db.session.commit()
            return product.to_dict()

        return None
