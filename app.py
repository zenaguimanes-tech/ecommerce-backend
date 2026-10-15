from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import os
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

app = Flask(__name__)
load_dotenv()
CORS(app, origins=["https://vercel.com/zenaguimanes-tech/ecommerce-frontend/B3oLEzAei8FgTDWjprwS83CCFzgj"])

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)


class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    description = db.Column(db.Text)
    image = db.Column(db.String(500))
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    category = db.relationship('Category', backref='products')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'price': float(self.price),
            'description': self.description,
            'image': self.image,
            'category_id': self.category_id,
            'category': self.category.name if self.category else None
        }


class CartItem(db.Model):
    __tablename__ = 'cart_items'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    quantity = db.Column(db.Integer, default=1)

    def to_dict(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'quantity': self.quantity
        }


with app.app_context():
    db.create_all()

'''
def load_products():
    if os.path.exists('products.json'):
        with open('products.json', 'r') as f:
            products = json.load(f)
            return products
    else:
        return []


def load_cart():
    if os.path.exists('cart.json'):
        with open('cart.json', 'r') as f:
            cart = json.load(f)
            return cart
    else:
        return []


def save_cart(cart):
    with open('cart.json', 'w') as f:
        json.dump(cart, f, indent=2)


def save_products(products):
    with open('products.json', 'w') as f:
        json.dump(products, f, indent=2)
'''


@app.route('/api/products', methods=['GET'])
def get_products():
    products = Product.query.all()
    return jsonify([p.to_dict() for p in products])


@app.route('/api/products/<int:id>', methods=['GET'])
def get_product(id):
    product = Product.query.get(id)
    if product:
        return jsonify(product.to_dict())
    return jsonify({'message': 'Product not found'}), 404


@app.route('/api/cart', methods=['GET'])
def get_cart():
    cart = CartItem.query.all()
    return jsonify([item.to_dict() for item in cart])


@app.route('/api/cart', methods=['POST'])
def add_to_cart():
    data = request.get_json()
    new_item = CartItem(product_id=data['product_id'], quantity=1)
    db.session.add(new_item)
    db.session.commit()
    return jsonify(new_item.to_dict()), 201


@app.route('/api/cart/<int:id>', methods=['DELETE'])
def delete_from_cart(id):
    item = CartItem.query.get(id)
    if item:
        db.session.delete(item)
        db.session.commit()
    return jsonify({'message': 'Item removed'})


@app.route('/api/products', methods=['POST'])
def post_products():
    data = request.get_json()
    new_product = Product(
        name=data['name'],
        price=data['price'],
        description=data['description'],
        image=data['image'],
        category_id=data.get('category_id')
    )
    db.session.add(new_product)
    db.session.commit()
    return jsonify(new_product.to_dict()), 201


@app.route('/api/products/<int:id>', methods=['PUT'])
def update_product(id):
    product = Product.query.get(id)
    data = request.get_json()
    if product:
        if 'name' in data:
            product.name = data['name']
        if 'image' in data:
            product.image = data['image']
        if 'description' in data:
            product.description = data['description']
        if 'price' in data:
            product.price = float(data['price'])
        if 'category_id' in data:
            product.category_id = data['category_id']
        db.session.commit()
        return jsonify(product.to_dict()), 200
    return jsonify({'message': 'Product not found'}), 404


@app.route('/api/products/<int:id>', methods=['DELETE'])
def delete_product(id):
    product = Product.query.get(id)
    if product:
        db.session.delete(product)
        db.session.commit()
        return jsonify({'message': 'Item deleted'})
    return jsonify({'message': 'Item not found'}), 404


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
