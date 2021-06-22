from datetime import datetime
from flaskblog import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_profile = db.Column(db.String(20), nullable=False, default='defaultProfile.jpg')
    password = db.Column(db.String(60), nullable=False)
    products = db.relationship('Product', backref='owner', lazy=True)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_profile}')"


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    store_id = db.Column(db.Integer, db.ForeignKey('store.id'), nullable=False)
    image_product = db.Column(db.String(20), nullable=False, default='defaultProduct.jpg')
    type = db.Column(db.String, nullable=False)
    price = db.Column(db.Integer, nullable=True)  # we should give a price when we choose a product for sale
    exchangeList = db.Column(db.String, nullable=True)  # we should give a list of exchange when we choose a product for exchange.

    def __repr__(self):
        return f"Product('{self.title}', '{self.date_posted}', '{self.image_product}', '{self.type}, '{self.price}', '{self.exchangeList}')"

class Store(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String, nullable=False)
    products = db.relationship('Product', backref='store', lazy=True)
    def __repr__(self):
        return f"Product('{self.name}', '{self.location}'"
