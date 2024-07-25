from functools import wraps
import os, re
from secrets import token_hex, compare_digest
from flask import render_template, request, redirect, url_for, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from groovekitchen import app
from groovekitchen.models import db, Caterer, Product, Cart, Customer, Wishlist, Like, Post, Comment, Booking


ALLOWED_EXTENSIONS_IMAGES = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'jpg', 'jfif'}
ALLOWED_EXTENSIONS_VIDEOS = {'mp4', 'mov', 'avi', 'mkv'}

def login_required(func):
    @wraps(func)
    def check_login(*args, **kwargs):
        if session.get('useronline') is not None:
            return func(*args, **kwargs)
        else:
            return redirect(url_for('login'))
    return check_login


@app.route('/caterer-details/<int:cid>/')
def caterer_details(cid):
    catererid = Caterer.query.filter(Caterer.id == cid).first()
    caterers = Caterer.query.all()
    # gallery = catererid.photos.split('*')
    if session.get('useronline'):
        cid = session.get('useronline')
        customer = Customer.query.get_or_404(cid)
        cart_items = Cart.query.filter_by(customerid=customer.id).all()
        number_of_cart_items = len(cart_items)
        wishlist_items = Wishlist.query.filter_by(customerid=customer.id).all()
        number_of_wishlist_item = len(wishlist_items)
    else:
        number_of_cart_items = 0
        number_of_wishlist_item = 0
        customer = None
    return render_template('caterers/caterer_details.html', title='Caterer Details', caterer=catererid, caterers=caterers, customer=customer, number_of_cart_items=number_of_cart_items,
                            number_of_wishlist_item=number_of_wishlist_item)


@app.route('/catering-services/')
def catering_services():
    caterers = Caterer.query.filter_by(status='1').all()
    if session.get('useronline'):
        cid = session.get('useronline')
        customer = Customer.query.get_or_404(cid)
        cart_items = Cart.query.filter_by(customerid=customer.id).all()
        wishlist_items = Wishlist.query.filter_by(customerid=customer.id).all()
        number_of_cart_items = len(cart_items)
        number_of_wishlist_item = len(wishlist_items)
    else:
        number_of_wishlist_item = 0
        number_of_cart_items = 0
        customer = None
    return render_template('caterers/catering_services.html', caterers=caterers, title='Professional Catering Services', page='catering',
                           number_of_wishlist_item=number_of_wishlist_item, number_of_cart_items=number_of_cart_items, customer=customer)


@app.route('/caterer-dashboard/')
@login_required
def caterer_dashboard():
    cid = session.get('useronline')
    catererid = Caterer.query.filter_by(customerid=cid).first()
    bookings = Booking.query.filter_by(caterer=catererid.id).all() or None
    total_bookings = len(bookings) if bookings else 0

    return render_template('caterers/dashboard.html', title='Dashboard', page="dashboard", caterer=catererid, total_bookings=total_bookings, bookings=bookings)


@app.route('/caterer-profile/')
@login_required
def caterer_profile():
    cid = session.get('useronline')
    catererid = Caterer.query.filter_by(customerid=cid).first()
    posts = Post.query.filter_by(posterid=catererid.customerid).all() or None
    products = Product.query.filter_by(customerid=cid, status='1').all() or None
    number_of_posts = len(posts) if posts else 0
    number_of_products = len(products) if products else 0
    return render_template('caterers/profile.html', title='My Profile', page="view-profile", caterer=catererid, number_of_products=number_of_products, number_of_posts=number_of_posts, posts=posts, products=products)


@app.route('/career-as-a-caterer/')
def caterer_career():
    if session.get('useronline'):
        cid = session.get('useronline')
        customer = Customer.query.get_or_404(cid)
        cart_items = Cart.query.filter_by(customerid=customer.id).all()
        wishlist_items = Wishlist.query.filter_by(customerid=customer.id).all()
        number_of_cart_items = len(cart_items)
        number_of_wishlist_item = len(wishlist_items)
    else:
        number_of_wishlist_item = 0
        number_of_cart_items = 0
        customer = None
    return render_template('caterers/caterers.html', title="Career as a caterer", number_of_wishlist_item=number_of_wishlist_item, number_of_cart_items=number_of_cart_items, customer=customer)


@app.route('/register-as-a-caterer/', methods=['GET', 'POST'])
def caterer_registration():
    if session.get('useronline'):
        cid = session.get('useronline')
        customer = Customer.query.get_or_404(cid) or None
        cart_items = Cart.query.filter_by(customerid=customer.id).all()
        wishlist_items = Wishlist.query.filter_by(customerid=customer.id).all()
        number_of_cart_items = len(cart_items)
        number_of_wishlist_item = len(wishlist_items)
    else:
        number_of_wishlist_item = 0
        number_of_cart_items = 0
        customer = None
    if request.method == 'POST':
        state = request.form.get('state')
        city = request.form.get('city')
        phone = request.form.get('phone')
        specialities = request.form.get('specialities')
        working_days = request.form.get('working_days')
        photo_file = request.files['photo']
        print(request.form)
       
        if state and city and phone and specialities and working_days and photo_file:
            file_name = photo_file.filename
            file_deets = file_name.split('.')
            ext = file_deets[-1]
            new_filename = token_hex(12) + '.' + ext
            photo_file.save('groovekitchen/static/photos/' + new_filename)

            caterer = Caterer(
                phone=phone,
                state=state,
                city=city,
                status='1',
                specialities=specialities,
                working_days=working_days,
                customerid=customer.id,
            )
            db.session.add(caterer)

            customer.dp=new_filename
            customer.customer_type='caterer'
            db.session.commit()
            return jsonify({"status": "success"})
        else:
            return jsonify({"status": "error"})
        
    return render_template('caterers/caterer_registration.html', title="Register as a caterer", customer=customer, number_of_cart_items=number_of_cart_items, number_of_wishlist_item=number_of_wishlist_item)


@app.route('/caterer-profile-setting/', methods=['GET', 'POST'])
@login_required
def caterer_profile_setting():
    cid = session.get('useronline')
    catererid = Caterer.query.filter_by(customerid=cid).first()
    customer = Customer.query.filter_by(id=catererid.customerid).first()
    if request.method == 'POST':
        firstname = request.form.get('firstname')
        lastname = request.form.get('lastname')
        state = request.form.get('state')
        city = request.form.get('city')
        email = request.form.get('email')
        phone = request.form.get('phone')
        specialities = request.form.get('specialities')
        working_days = request.form.get('working_days')
        dp_file = request.files['photo']
        
        if firstname and lastname and state and city and email and phone and specialities and working_days :
            if dp_file:
                file_name = dp_file.filename
                file_deets = file_name.split('.')
                ext = file_deets[-1]
                new_filename = token_hex(10) + '.' + ext
                dp_file.save('groovekitchen/static/photos/' + new_filename)
            else:
                new_filename = customer.dp

            
            catererid.state = state
            catererid.city = city
            catererid.phone = phone
            catererid.specialities = specialities
            catererid.working_days = working_days
            customer.email = email
            customer.lastname = lastname
            customer.firstname = firstname
            customer.dp = new_filename
            
            db.session.commit()
            return jsonify({"status": "success"})
        else:
            return jsonify({"message":"Please complete all data fields!", "status": "error"})
    
    return render_template('caterers/profile_setting.html', title='Profile Setting', page="profile-setting", caterer=catererid)


@app.route('/caterer-account-setting/', methods=['GET', 'POST'])
@login_required
def caterer_account_setting():
    cid = session.get('useronline')
    catererid = Caterer.query.filter_by(customerid=cid).first()
    customer = Customer.query.filter_by(id=catererid.customerid).first()
    if request.method == 'POST':
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if password and confirm_password:
            if compare_digest(password, confirm_password) is True:
                hash_pwd = generate_password_hash(password)
                customer.password=hash_pwd
                db.session.commit()
                return jsonify({"status": "success"})
            else:
                return jsonify({"status": "unmatch_password"})
        return jsonify({"status": "error"})
    return render_template('caterers/account_setting.html', title='Account Setting', page="account-setting", caterer=catererid)


@app.route('/caterer-delete-account/<int:cid>/')
@login_required
def caterer_delete_account(cid):
    cid = session.get('useronline')
    catererid = Caterer.query.filter_by(customerid=cid).first()
    
    catererid.status='0'
    db.session.commit()
    
    return jsonify({"status": "delete"})


@app.route('/caterer-deactivate-account/<int:cid>/')
@login_required
def caterer_deactivate_account(cid):
    cid = session.get('useronline')
    catererid = Caterer.query.filter_by(customerid=cid).first()
    
    catererid.status = '2'
    db.session.commit()
    
    return jsonify({"status": "deactivate"})


@app.route('/caterer-logout/')
@login_required
def caterer_logout():
    if session.get('useronline'):
        session.pop('useronline')
        session.clear()
    return redirect(url_for('login'))


@app.route('/view-caterer-profile/')
@login_required
def view_caterer_profile():
    cid = session.get('useronline')
    catererid = Caterer.query.filter_by(customerid=cid).first()
    return render_template("caterers/view_caterer_profile.html", title="View Profile", caterer=catererid)


@app.route('/caterer-timeline/')
def caterer_timeline():
    cid = session.get('useronline')
    catererid = Caterer.query.filter_by(customerid=cid).first()
    likes = Like.query.all()
    customer_on_list = Like.query.filter_by(customerid=catererid.id).first()
    posts = Post.query.filter_by(posterid=catererid.customerid).order_by(Post.date_posted.desc()).all()
    comments = Comment.query.all()
    return render_template('caterers/timeline.html', title='Timeline', caterer=catererid, posts=posts, customer_on_list=customer_on_list, comments=comments, likes=likes)


@app.route('/caterer-make-post/', methods=['GET', 'POST'])
@login_required
def caterer_make_post():
    cid = session.get('useronline')
    catererid = Caterer.query.filter_by(customerid=cid).first()
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        file = request.files['mediaFile']
        if file and content and title:
            file_name = file.filename
            file_deets = file_name.split('.')
            ext = file_deets[-1]
            
            if ext in ALLOWED_EXTENSIONS_IMAGES:
                new_filename = token_hex(16) + '.' + ext
                file.save('groovekitchen/static/media/' + new_filename)
                file_type = "image"    
            elif ext in ALLOWED_EXTENSIONS_VIDEOS:
                new_filename = token_hex(16) + '.' + ext
                video_path = 'groovekitchen/static/media/' + new_filename
                file.save(video_path)
                duration = get_video_duration(video_path)
                if duration <= 30:
                    new_filename = new_filename
                    file_type = "video"
                else:
                    return jsonify({"message":"Video duration must be 30 secs max", "status": "large_file"})
            else:
                return jsonify({"status": "not-allowd", "message": "File type is not allowed."})
                
            post = Post(title=title, content=content, file_type=file_type, category='caterer', file=new_filename, posterid=catererid.customerid)
            db.session.add(post)
            db.session.commit()
            return jsonify({"status": "success"})
        else:
            return jsonify({"status": "error"})
    return render_template("caterers/caterer_make_post.html", title="Social Fields", caterer=catererid)


@app.route('/caterer-create-product/', methods=['GET', 'POST'])
@login_required
def caterer_create_product():
    cid = session.get('useronline')
    catererid = Caterer.query.filter_by(customerid=cid).first()
    if request.method == 'POST':
        product_name = request.form.get('product_name')
        price = request.form.get('price')
        desc = request.form.get('desc')
        photos = request.files.getlist('photos')

        if product_name and price and desc and photos:
            image_list = []
            for photo in photos[:4]:
                file_name = photo.filename
                ext = os.path.splitext(file_name)[1] 
                new_filename = token_hex(16) + ext
                photo.save('groovekitchen/static/products/' + new_filename)
                image_list.append(new_filename)
           
            images = '*'.join(image_list)
            product = Product(name=product_name, price=price, status='1', image=images, description=desc, customerid=cid)
            db.session.add(product)
            db.session.commit()
            return jsonify({"status": "success"})
        else:
            return jsonify({"status": "error"})
    return render_template('caterers/create_product.html', title='Create Product', caterer=catererid)


@app.route('/caterer-product/')
def caterer_product():
    cid = session.get('useronline')
    catererid = Caterer.query.filter_by(customerid=cid).first()
    products = Product.query.filter_by(customerid=cid, status='1').all()
    return render_template('caterers/products.html', title="My Products", caterer=catererid, products=products)


@app.route('/caterer-delete-product/<int:pid>/')
def caterer_delete_product(pid):
    return 'pass'


@app.route('/caterer-view-count/<int:id>/', methods=['GET', 'POST'])
def caterer_profile_view_count(id):
    caterer = Caterer.query.get_or_404(id)
    caterer.view_count += 1
    db.session.commit()
    return jsonify({"status": "success"})