from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    image = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.Enum('0', '1'), default=1)
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    date_updated = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    # setting foreign keys
    customerid = db.Column(db.Integer, db.ForeignKey('customers.id', ondelete='CASCADE'))

    # setting relationship
    cart_deets = db.relationship('Cart', back_populates='product_deets', lazy=True, cascade='all, delete', passive_deletes=True)
    customer_deets = db.relationship('Customer', back_populates='product_deets', lazy=True, cascade='all, delete', passive_deletes=True)
    wishlist_deets = db.relationship('Wishlist', back_populates='product_deets', lazy=True, cascade='all, delete', passive_deletes=True)
    orderitem_deets = db.relationship('OrderItem', back_populates='product_deets', lazy=True, cascade='all, delete', passive_deletes=True)

class Cart(db.Model):
    cart_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    quantity = db.Column(db.Integer, default=1)
    
    # setting foreign keys
    customerid = db.Column(db.Integer, db.ForeignKey('customers.id', ondelete='CASCADE'))
    productid = db.Column(db.Integer, db.ForeignKey('products.id', ondelete='CASCADE'))
    
    # setting relationship
    product_deets = db.relationship('Product', back_populates='cart_deets', lazy=True, cascade='all, delete', passive_deletes=True)
    
class Customer(db.Model):
    __tablename__ = 'customers'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    firstname = db.Column(db.String(50), nullable=False)
    lastname = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=True)
    date_registered = db.Column(db.DateTime, default=datetime.utcnow)
    dp = db.Column(db.String(255), nullable=True)
    customer_type = db.Column(db.Enum('chef', 'caterer', 'agent', 'customer'), default='customer')
    # setting foreignkey

    # setting relationship
    order_deets = db.relationship('Order', back_populates='customer_deets', lazy=True, cascade='all, delete', passive_deletes=True)
    product_deets = db.relationship('Product', back_populates='customer_deets', lazy=True, cascade='all, delete', passive_deletes=True)
    payment_deets = db.relationship('Payment', back_populates='customer_deets', lazy=True, cascade='all, delete', passive_deletes=True)
    post_deets = db.relationship('Post', back_populates='customer_deets', lazy=True, cascade='all, delete', passive_deletes=True)
    chef_deets = db.relationship('Chef', back_populates='customer_deets', lazy=True, cascade='all, delete', passive_deletes=True)
    caterer_deets = db.relationship('Caterer', back_populates='customer_deets', lazy=True, cascade='all, delete', passive_deletes=True)
    agent_deets = db.relationship('CommunityAgent', back_populates='customer_deets', lazy=True, cascade='all, delete', passive_deletes=True)
    comment_deets = db.relationship('Comment', back_populates='customer_deets', lazy=True, cascade='all, delete', passive_deletes=True)
    booking_deets = db.relationship('Booking', back_populates='customer_deets', lazy=True, cascade='all, delete', passive_deletes=True)
    
class Chef(db.Model):
    __tablename__ = 'chefs'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    phone = db.Column(db.String(15), nullable=False)
    city = db.Column(db.String(50), nullable=False)
    state = db.Column(db.String(30), nullable=False)
    working_days = db.Column(db.String(200), nullable=False)
    view_count = db.Column(db.Integer, default=0)
    verification = db.Column(db.Enum('verified', 'unverified'), default='unverified')
    status = db.Column(db.Enum('0', '1', '2'), default=1)
    date_registered = db.Column(db.DateTime, default=datetime.utcnow)
    date_updated = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    # setting foreignkey
    specialityid = db.Column(db.Integer, db.ForeignKey('speciality.id', ondelete='CASCADE'))
    customerid = db.Column(db.Integer, db.ForeignKey('customers.id', ondelete='CASCADE'))

    # setting relationship
    customer_deets = db.relationship('Customer', back_populates='chef_deets', lazy=True, cascade='all, delete', passive_deletes=True)
    speciality_deets = db.relationship('Speciality', back_populates='chef_deets', lazy=True, cascade='all, delete', passive_deletes=True)
        
class Caterer(db.Model):
    __tablename__ = 'caterers'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    phone = db.Column(db.String(15), nullable=False)
    city = db.Column(db.String(50), nullable=False)
    state = db.Column(db.String(30), nullable=False)
    working_days = db.Column(db.String(255), nullable=False)
    view_count = db.Column(db.Integer, default=0)
    status = db.Column(db.Enum('0', '1', '2'), default=1)
    verification = db.Column(db.Enum('verified', 'unverified'), default='unverified')
    date_registered = db.Column(db.DateTime, default=datetime.utcnow)
    date_updated = db.Column(db.DateTime, onupdate=datetime.utcnow)
   
    # setting foreignkey
    customerid = db.Column(db.Integer, db.ForeignKey('customers.id', ondelete='CASCADE'))
    specialityid = db.Column(db.Integer, db.ForeignKey('speciality.id', ondelete='CASCADE'))
    
    # setting relationships
    customer_deets = db.relationship('Customer', back_populates='caterer_deets', lazy=True, cascade='all, delete', passive_deletes=True)
    speciality_deets = db.relationship('Speciality', back_populates='caterer_deets', lazy=True, cascade='all, delete', passive_deletes=True)
    gallery_deets = db.relationship('Gallery', back_populates='caterer_deets', lazy=True, cascade='all, delete', passive_deletes=True)

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    firstname = db.Column(db.String(50), nullable=False)
    lastname = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True)
    ref = db.Column(db.String(255), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    date_paid = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.Enum('pending', 'failed', 'paid'), server_default='pending')
    
    # setting foreignkeys
    customerid = db.Column(db.Integer, db.ForeignKey('customers.id', ondelete='CASCADE'))

    # setting relationships
    customer_deets = db.relationship('Customer', back_populates='payment_deets', lazy=True, cascade='all, delete', passive_deletes=True)
    order_deets = db.relationship('Order', back_populates='payment_deets', lazy=True, cascade='all, delete', passive_deletes=True)

class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    order_number = db.Column(db.String(255), nullable=False)
    date_ordered = db.Column(db.DateTime, default=datetime.utcnow)
    
    # setting foreignkeys
    customerid = db.Column(db.Integer, db.ForeignKey('customers.id', ondelete='CASCADE'))
    paymentid = db.Column(db.Integer, db.ForeignKey('payment.id', ondelete='CASCADE'))
    
    # setting relationships
    customer_deets = db.relationship('Customer', back_populates='order_deets', lazy=True, cascade='all, delete', passive_deletes=True)
    payment_deets = db.relationship('Payment', back_populates='order_deets', lazy=True, cascade='all, delete', passive_deletes=True)   
    orderitem_deets = db.relationship('OrderItem', back_populates='order_deets', lazy=True, cascade='all, delete', passive_deletes=True)

class OrderItem(db.Model):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    
    # setting foreignkeys
    orderid = db.Column(db.Integer, db.ForeignKey('orders.id', ondelete='CASCADE'))
    productid = db.Column(db.Integer, db.ForeignKey('products.id', ondelete='CASCADE'))
    quantity = db.Column(db.Integer, default=1)
    price_per_unit = db.Column(db.Float)
    
    # setting relationships
    order_deets = db.relationship('Order', back_populates='orderitem_deets', lazy=True, cascade='all, delete', passive_deletes=True)
    product_deets = db.relationship('Product', back_populates='orderitem_deets', lazy=True, cascade='all, delete', passive_deletes=True)

class Wishlist(db.Model):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    wishlist_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # setting foreignkeys
    customerid = db.Column(db.Integer, db.ForeignKey('customers.id', ondelete='CASCADE'))
    productid = db.Column(db.Integer, db.ForeignKey('products.id', ondelete='CASCADE'))
    
    # setting relationships
    product_deets = db.relationship('Product', back_populates='wishlist_deets', lazy=True, cascade='all, delete', passive_deletes=True)
     
class Post(db.Model):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    file = db.Column(db.String(255), nullable=False)
    file_type = db.Column(db.Enum('image', 'video'), nullable=False)
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    likes_count = db.Column(db.Integer, default=0)
    category = db.Column(db.Enum('chef', 'caterer'), nullable=False)
    
    # Setting foreign key
    posterid = db.Column(db.Integer, db.ForeignKey('customers.id', ondelete='CASCADE'))
    
    
    # Setting Relationship
    customer_deets = db.relationship('Customer', back_populates='post_deets', lazy=True, cascade='all, delete', passive_deletes=True)
    like_deets = db.relationship('Like', back_populates='post_deets', lazy=True, cascade='all, delete', passive_deletes=True)

class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    comment_date = db.Column(db.DateTime, default=datetime.utcnow)

    # Setting foreign key
    commenterid = db.Column(db.Integer, db.ForeignKey('customers.id', ondelete='CASCADE'))
    postid = db.Column(db.Integer, db.ForeignKey('post.id', ondelete='CASCADE'))

    # setting relationships
    customer_deets = db.relationship('Customer', back_populates='comment_deets', lazy=True, cascade='all, delete', passive_deletes=True)

class Like(db.Model):
    __tablename__ = 'likes'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    like_date = db.Column(db.DateTime, default=datetime.utcnow)

    # Setting foreign key
    customerid = db.Column(db.Integer, db.ForeignKey('customers.id', ondelete='CASCADE'))
    postid = db.Column(db.Integer, db.ForeignKey('post.id', ondelete='CASCADE'))

    # setting relationships
    customer_deets = db.relationship('Customer', backref='like_deets', lazy=True, cascade='all, delete', passive_deletes=True)
    post_deets = db.relationship('Post', back_populates='like_deets', lazy=True, cascade='all, delete', passive_deletes=True)

class CommunityAgent(db.Model):
    __tablename__ = 'agents'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    address = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    state = db.Column(db.String(30), nullable=False)
    city = db.Column(db.String(50), nullable=False)
    verification = db.Column(db.Enum('verified', 'unverified'), default='unverified')
    view_count = db.Column(db.Integer, default=0)
    status = db.Column(db.Enum('0', '1', '2'), default=1)
    date_registered = db.Column(db.DateTime, default=datetime.utcnow)
    date_updated = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    # setting foreignkey
    customerid = db.Column(db.Integer, db.ForeignKey('customers.id', ondelete='CASCADE'))
    specialityid = db.Column(db.Integer, db.ForeignKey('speciality.id', ondelete='CASCADE'))
    
    # setting relationship
    customer_deets = db.relationship('Customer', back_populates='agent_deets', lazy=True, cascade='all, delete', passive_deletes=True)
    speciality_deets = db.relationship('Speciality', back_populates='agent_deets', lazy=True, cascade='all, delete', passive_deletes=True)
        
class Gallery(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    description = db.Column(db.String(255), nullable=True)
    image = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    date_updated = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    # setting foreign keys
    catererid = db.Column(db.Integer, db.ForeignKey('caterers.id', ondelete='CASCADE'))

    # setting relationship
    caterer_deets = db.relationship('Caterer', back_populates='gallery_deets', lazy=True, cascade='all, delete', passive_deletes=True)

class Booking(db.Model):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    address = db.Column(db.String(255), nullable=False)
    message = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    # setting foreignkeys
    chef = db.Column(db.Integer, db.ForeignKey('chefs.id', ondelete='CASCADE'), nullable=True)
    caterer = db.Column(db.Integer, db.ForeignKey('caterers.id', ondelete='CASCADE'), nullable=True)
    booker = db.Column(db.Integer, db.ForeignKey('customers.id', ondelete='CASCADE'))
    
    # setting relationships
    customer_deets = db.relationship('Customer', back_populates='booking_deets', lazy=True, cascade='all, delete', passive_deletes=True)

class Menu(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    image = db.Column(db.String(255), nullable=False)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    date_updated = db.Column(db.DateTime, onupdate=datetime.utcnow)

    # setting relationship
    menuitem_deets = db.Relationship('MenuItem', back_populates='menu_deets', lazy=True, cascade='all, delete', passive_deletes=True)

class MenuItem(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    date_updated = db.Column(db.DateTime, onupdate=datetime.utcnow) 

    # setting foreignkkey
    menuid = db.Column(db.Integer, db.ForeignKey('menu.id', ondelete='CASCADE'))

    # setting relationship
    menu_deets = db.Relationship('Menu', back_populates='menuitem_deets', lazy=True, cascade='all, delete', passive_deletes=True)

class Speciality(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    date_updated = db.Column(db.DateTime, onupdate=datetime.utcnow) 

    # setting relationship
    chef_deets = db.Relationship('Chef', back_populates='speciality_deets', lazy=True, cascade='all, delete', passive_deletes=True)
    caterer_deets = db.Relationship('Caterer', back_populates='speciality_deets', lazy=True, cascade='all, delete', passive_deletes=True)
    agent_deets = db.Relationship('CommunityAgent', back_populates='speciality_deets', lazy=True, cascade='all, delete', passive_deletes=True)