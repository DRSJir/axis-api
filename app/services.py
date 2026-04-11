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
    def get_cart_summary(session_id, user_id=None):
        # si el ID está vacío, no consultamos la DB
        if not session_id or str(session_id).strip() == "" or session_id == "undefined":
            return {
                "items": [],
                "calculation": {
                    "subtotal": 0,
                    "tax": 0,
                    "shipping": 0,
                    "total": 0
                }
            }

        # si el ID es válido, procedemos con la consulta normal
        query = CartItem.query.filter(
            (CartItem.user_id == user_id) if user_id else (CartItem.session_id == session_id)
        )
        items = query.all()

        subtotal = sum(item.product.price * item.quantity for item in items)
        tax = round(subtotal * CartService.TAX_RATE, 2)

        return {
            "items": [item.to_dict() for item in items],
            "calculation": {
                "subtotal": round(subtotal, 2),
                "tax": tax,
                "shipping": CartService.SHIPPING_FEE,
                "total": round(subtotal + tax + CartService.SHIPPING_FEE, 2)
            }
        }

    @staticmethod
    def add_to_cart(product_id, quantity, session_id, user_id=None):
        try:
            quantity = int(quantity)
            product = Product.query.get(product_id)

            # validación de existencia
            if not product:
                return {"error": "Producto no encontrado", "status": 404}

            # validación de disponibilidad inicial
            if product.stock < quantity:
                return {
                    "error": "Disponibilidad insuficiente",
                    "requested": quantity,
                    "available": product.stock,
                    "status": 400
                }

            # Buscar si el producto ya está en el carrito de ESTA sesión/usuario
            item = CartItem.query.filter_by(
                product_id=product_id,
                session_id=session_id
            ).first()

            if item:
                # validar que la suma no exceda el stock real
                if (item.quantity + quantity) > product.stock:
                    return {
                        "error": f"No puedes agregar más. Stock máximo: {product.stock}",
                        "status": 400
                    }
                item.quantity += quantity
                # si el usuario se logueó a mitad de sesión, actualizamos su user_id
                if user_id:
                    item.user_id = user_id
            else:
                # crear nuevo registro vinculado a la sesión
                item = CartItem(
                    product_id=product_id,
                    quantity=quantity,
                    session_id=session_id,
                    user_id=user_id
                )
                db.session.add(item)

            db.session.commit()
            return {
                "message": "Producto agregado con éxito",
                "item": item.to_dict(),
                "status": 200
            }

        except Exception as e:
            db.session.rollback()  # Corregido: db.session.rollback
            return {"error": f"Error interno: {str(e)}", "status": 500}

    @staticmethod
    def complete_checkout(session_id, user_id=None):
        # obtener solo los items de esta sesión
        cart_items = CartItem.query.filter_by(session_id=session_id).all()

        if not cart_items:
            return {"error": "El carrito está vacío", "status": 400}

        try:
            # validar stock final para cada item (Atomicidad)
            for item in cart_items:
                if item.product.stock < item.quantity:
                    return {
                        "error": f"Stock insuficiente para {item.product.name}",
                        "available": item.product.stock,
                        "status": 409,
                    }

            # obtener resumen para el historial y recibo
            summary = CartService.get_cart_summary(session_id, user_id)

            # crear el registro en el Historial de Órdenes (Fase 2+)
            from app.models import Order  # Importación local para evitar ciclos
            new_order = Order(
                user_id=user_id,
                total=summary['calculation']['total'],
                # Guardamos un snapshot de los nombres y precios actuales
                items_json=[{
                    "name": item.product.name,
                    "price": item.product.price,
                    "quantity": item.quantity,
                    "sku": item.product.sku
                } for item in cart_items]
            )
            db.session.add(new_order)

            # descontar stock y limpiar el carrito de esta sesión
            for item in cart_items:
                item.product.stock -= item.quantity
                db.session.delete(item)

            db.session.commit()

            return {
                "message": "Orden procesada con éxito",
                "order_id": new_order.id,
                "receipt": summary['calculation'],
                "status": 201
            }

        except Exception as e:
            db.session.rollback()
            return {
                "error": f"Error al procesar la compra: {str(e)}",
                "status": 500
            }
