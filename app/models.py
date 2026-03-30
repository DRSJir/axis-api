from .database import db

class Device(db.Model):
    __tablename__ = 'device'
    id = db.Column(db.Integer, primary_key=True)
    model_name = db.Column(db.String(50), unique=True, nullable=False)

product_compatibility = db.Table('product_compatibility',
    db.Column('product_id', db.Integer, db.ForeignKey('product.id'), primary_key=True),
    db.Column('device_id', db.Integer, db.ForeignKey('device.id'), primary_key=True)
)

class Category(db.Model):
    __tablename__ = 'category'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    products = db.relationship('Product', backref='category', lazy=True)


class Product(db.Model):
    __tablename__ = 'product'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, default=0)
    material = db.Column(db.String(100))
    sku = db.Column(db.String(20), unique=True)

    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)

    compatible_devices = db.relationship('Device',
        secondary=product_compatibility,
        backref=db.backref('products', lazy='dynamic')
    )

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category.name if self.category else "sin categoría",
            "description": self.description,
            "price": self.price,
            "stock": self.stock,
            "material": self.material,
            "sku": self.sku,
            "compatibility": [d.model_name for d in self.compatible_devices]
        }


class CartItem(db.Model):
    __tablename__ = 'cart_item'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)

    product = db.relationship('Product', backref='cart_items')

    def to_dict(self):
        return {
            "id": self.id,
            "product_id": self.product_id,
            "name": self.product.name,
            "price": self.product.price,
            "quantity": self.quantity,
            "subtotal": round(self.product.price * self.quantity, 2)
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
