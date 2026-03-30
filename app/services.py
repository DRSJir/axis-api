from itertools import product

from unicodedata import category

from app.database import db
from app.models import Product, Category, Device


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
        existing_sku = Product.query.filter_by(sku=data['sku']).first()
        if existing_sku:
            return {"error": f"el sku '{data['sku']}' ya esta registrado", "status": 409}

        try:
            # Buscar la categoría
            category_name = data.get('category')
            category = Category.query.filter_by(name=category_name).first()

            # Crear la categoria si no existe
            if not category:
                category = Category(name=category_name)
                db.session.add(category)

            # Crear la instancia básica del Producto
            new_prod = Product(
                name=data["name"],
                price=data["price"],
                stock=data["stock"],
                sku=data["sku"],
                material=data.get('material'),
                category=category
            )

            # Vincular dispositivos disponibles compatibles
            device_names = data.get('compatibility', [])
            for model in device_names:
                device = Device.query.filter_by(model_name=model).first()
                if not device:
                    device = Device(model_name=model)
                    db.session.add(device)

                new_prod.compatible_devices.append(device)

            db.session.add(new_prod)
            db.session.commit()
            result = new_prod.to_dict()
            result['status'] = 201
            return result

        except Exception as e:
            db.session.rollback()
            return {"Error": "Error en la creación", "estatus": 500}

    @staticmethod
    def get_all_products():
        products = Product.query.all()
        return [product.to_dict() for product in products]

    @staticmethod
    def get_product_by_id(id):
        product = Product.query.get(id)
        return product.to_dict() if product else None

    @staticmethod
    def update_product_stock(id, new_stock):
        product = Product.query.get(id)
        if product:
            product.stock = new_stock
            db.session.commit()
            return product.to_dict()

        return None

    @staticmethod
    def get_filtered_catalog(category_name=None, model_name=None):
        query = Product.query

        # Filtro por categoría
        if category_name:
            query = query.join(Category).filter(Category.name == category_name)

        # Filtro por modelo de dispositivo
        if model_name:
            query = query.join(Product.compatible_devices).filter(Device.model_name == model_name)

        products = query.all()
        return [product.to_dict() for product in products]
