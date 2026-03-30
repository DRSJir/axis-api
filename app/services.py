from app.database import db
from app.models import Product, Category, Device, CartItem


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
    def get_filtered_catalog(category_name=None, model_name=None, search_query=None):
        query = Product.query

        # Filtro por categoría
        if category_name:
            query = query.join(Category).filter(Category.name == category_name)

        # Filtro por modelo de dispositivo
        if model_name:
            query = query.join(Product.compatible_devices).filter(Device.model_name == model_name)

        # Busqueda por nombre
        if search_query:
            query = query.filter(Product.name.ilike(f"{search_query}%"))

        products = query.all()
        return [product.to_dict() for product in products]

    @staticmethod
    def get_paginated_catalog(category_name=None, model_name=None, search_query=None, page=1, per_page=10):
        query = Product.query

        # Filtro por categoría
        if category_name:
            query = query.join(Category).filter(Category.name == category_name)

        # Filtro por modelo de dispositivo
        if model_name:
            query = query.join(Product.compatible_devices).filter(Device.model_name == model_name)

        # Búsqueda por nombre
        if search_query:
            query = query.filter(Product.name.ilike(f"{search_query}%"))

        # Paginación
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)

        return {
            "items": [p.to_dict() for p in pagination.items],
            "total": pagination.total,
            "pages": pagination.pages,
            "current_page": pagination.page,
            "next_page": pagination.next_num,
            "prev_page": pagination.prev_num,
            "has_next": pagination.has_next,
            "has_prev": pagination.has_prev
        }


class CartService:
    TAX_RATE = 0.16
    SHIPPING_FEE = 0.15

    @staticmethod
    def get_cart_summary():
        items = CartItem.query.all()
        subtotal = sum((item.product.price * item.quantity) for item in items)
        tax = subtotal * CartService.TAX_RATE
        total = subtotal + tax + (CartService.SHIPPING_FEE if subtotal > 0 else 0)

        return {
            "items": [item.to_dict() for item in items],
            "calculation": {
                "subtotal": round(subtotal, 2),
                "tax": round(tax, 2),
                "shipping": CartService.SHIPPING_FEE if total > 0 else 0,
                "total": round(total, 2)
            }
        }

    @staticmethod
    def add_to_cart(product_id, quantity):
        quantity = int(quantity)
        product = Product.query.get(product_id)

        # 1. Verificar si el producto existe
        if not product:
            return {
                "error": "producto no encontrado",
                "status": 404
            }

        # 2. Validación de Disponibilidad (Regla de Negocio)
        if product.stock < quantity:
            return {
                "error": "disponibilidad insuficiente",
                "requested": quantity,
                "available": product.stock,
                "status": 400
            }

        # 3. Verificar si ya está en el carrito para actualizar cantidad o crear nuevo
        try:
            item = CartItem.query.filter_by(product_id = product_id).first()
            if item:
                # Suma total no exede el total
                if (item.quantity + quantity) > product.stock:
                    return {
                        "error": "disponibilidad insuficiente",
                        "status": 400
                    }
                item.quantity += quantity

            else:
                item = CartItem(product_id=product_id, quantity=quantity)
                db.session.add(item)

            db.session.commit()
            return {"message": "producto agregado con exito", "status": 200}

        except Exception as e:
            db.rollback()
            return {"error": f"{e}", "status": 200}

    @staticmethod
    def complete_checkout():
        # Obtener todos los elementos del carrito
        cart_items = CartItem.query.all()

        if not cart_items:
            return {"error": "el carrito esta vacio", "status": 400}

        try:
            # Validar stock para cada producto
            for item in cart_items:
                if item.product.stock < item.quantity:
                    return {
                        "error": "stock insificiente",
                        "available": item.quantity,
                        "status": 409,
                    }

            # cuando todos tienen stock
            summary = CartService.get_cart_summary()

            for item in cart_items:
                item.product.stock -= item.quantity
                db.session.delete(item) # Limpiar el carrito

            db.session.commit()

            return {
                "message": "orden procesada",
                "recipt": summary['calculation'],
                "status": 201
            }

        except Exception as e:
            db.session.rollback()
            return {
                "error": f"error al procesar la compra {str(e)}",
                "status": 500
            }
