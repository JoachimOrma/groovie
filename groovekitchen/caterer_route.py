from functools import wraps
import os, re, random
from secrets import token_hex, compare_digest
from flask import render_template, request, redirect, url_for, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import joinedload
from sqlalchemy import or_
from groovekitchen import app
from groovekitchen.models import db, Caterer, Product, Cart, Customer, Wishlist, Like, Post, Speciality, Comment, Booking, Gallery


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
    catererid.view_count += 1
    db.session.commit()
    caterers = Caterer.query.all()
    cid = session.get('useronline')
    if cid:
        customer = Customer.query.get_or_404(cid)
        number_of_cart_items = Cart.query.filter_by(customerid=customer.id).count()
    customer = None
    number_of_cart_items = 0
    return render_template('caterers/caterer_details.html',
        title='Caterer Details',
        caterer=catererid,
        caterers=caterers,
        customer=customer,
        number_of_cart_items=number_of_cart_items
    )


@app.route('/get-caterers/')
def get_caterers():
    caterers = Caterer.query.filter_by(status='1', verification='unverified').all()
    if caterers:
        random.shuffle(caterers)
        caterer_list = [{
            "id": caterer.id,
            "customerid": caterer.customerid,
            "firstname": caterer.customer_deets.firstname,
            "lastname": caterer.customer_deets.lastname,
            "dp": caterer.customer_deets.dp,
            "specialities": caterer.specialities,
            "city": caterer.city,
            "state": caterer.state,
        } for caterer in caterers]
        return jsonify({"status": "success", "caterer_list": caterer_list})
    else:
        return jsonify({"status": "not-found"})


@app.route('/catering-services/', methods=['GET', 'POST'])
def catering_services():    
    if request.method == 'POST':
        search_input = request.form.get('searchInput')
        if search_input:
            random.shuffle(caterer)
            caterers = Caterer.query.join(Customer).filter(
                or_(
                    Customer.firstname.ilike(f'%{search_input}%'),
                    Customer.lastname.ilike(f'%{search_input}%'),
                    Caterer.city.ilike(f'%{search_input}%'),
                    Caterer.state.ilike(f'%{search_input}%'),
                    Caterer.specialities.ilike(f'%{search_input}%')
                ), Caterer.status == '1', Caterer.verification == 'unverified').all()
            if caterers:
                caterer_list = [{
                    "id": caterer.id,
                    "customerid": caterer.customerid,
                    "firstname": caterer.customer_deets.firstname,
                    "lastname": caterer.customer_deets.lastname,
                    "dp": caterer.customer_deets.dp,
                    "specialities": caterer.specialities,
                    "city": caterer.city,
                    "state": caterer.state,
                } for caterer in caterers]

                return jsonify({"status": "success", "caterer_list": caterer_list})
            else:
                return jsonify({"status": "not-found"})
        else:
            return jsonify({"status": "error"})
    else:
        search = "E.g: Lola or Osun or Asian Dishes"
        text = "Find professional caterers around you."
        gallery = Gallery.query.all()
        cid = session.get('useronline')
        if cid:
            customer = Customer.query.get_or_404(cid)
            number_of_cart_items = Cart.query.filter_by(customerid=customer.id).count()
        customer = None
        number_of_cart_items = 0
    return render_template('caterers/catering_services.html',
            title='Caterers & Event Planners',
            search=search,
            text=text,
            page='catering',
            gallery=gallery,
            number_of_cart_items=number_of_cart_items,
            customer=customer
        )


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
    cid = session.get('useronline')
    if cid:
        customer = Customer.query.get_or_404(cid)
        number_of_cart_items = Cart.query.filter_by(customerid=customer.id).count()
    customer = None
    number_of_cart_items = 0
    return render_template('caterers/caterers.html',
        title="Career as a caterer",
        number_of_cart_items=number_of_cart_items,
        customer=customer
    )


@app.route('/register-as-a-caterer/', methods=['GET', 'POST'])
def caterer_registration():
    if request.method == 'POST':
        state = request.form.get('state')
        city = request.form.get('city')
        phone = request.form.get('phone')
        speciality = request.form.get('specialities')
        working_days = request.form.get('working_days')
        photo_file = request.files['photo']
        print(request.form)
       
        if state and city and phone and speciality and working_days and photo_file:
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
                specialityid=speciality,
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
    else:
        specialities = Speciality.query.all()
        cid = session.get('useronline')
        if cid:
            customer = Customer.query.get_or_404(cid)
            number_of_cart_items = Cart.query.filter_by(customerid=customer.id).count()
        customer = None
        number_of_cart_items = 0
    return render_template('caterers/caterer_registration.html',
        title="Register as a caterer",
        customer=customer,
        number_of_cart_items=number_of_cart_items,
        specialities=specialities,     
    )


@app.route('/caterer-profile-setting/', methods=['GET', 'POST'])
@login_required
def caterer_profile_setting():
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
    else:
        cid = session.get('useronline')
        catererid = Caterer.query.filter_by(customerid=cid).first()
        customer = Customer.query.filter_by(id=catererid.customerid).first()  
    return render_template('caterers/profile_setting.html',
        title='Profile Setting',
        page="profile-setting",
        caterer=catererid
    )


@app.route('/caterer-account-setting/', methods=['GET', 'POST'])
@login_required
def caterer_account_setting():   
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
    else:
        cid = session.get('useronline')
        catererid = Caterer.query.filter_by(customerid=cid).first()
        customer = Customer.query.filter_by(id=catererid.customerid).first()
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


@app.route('/caterer-timeline/')
@login_required
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
    else:
        cid = session.get('useronline')
        catererid = Caterer.query.filter_by(customerid=cid).first()
    return render_template("caterers/caterer_make_post.html", title="Social Fields", caterer=catererid)


@app.route('/caterer-create-product/', methods=['GET', 'POST'])
@login_required
def caterer_create_product():
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
    else:
        cid = session.get('useronline')
        catererid = Caterer.query.filter_by(customerid=cid).first()
    return render_template('caterers/create_product.html', title='Create Product', caterer=catererid)


@app.route('/caterer-product/')
@login_required
def caterer_product():
    cid = session.get('useronline')
    catererid = Caterer.query.filter_by(customerid=cid).first()
    products = Product.query.filter_by(customerid=cid, status='1').all()
    return render_template('caterers/products.html', title="My Products", caterer=catererid, products=products)


@app.route('/caterer-delete-product/<int:pid>/')
@login_required
def caterer_delete_product(pid):
    return 'pass'

@app.route('/caterer-gallery/', methods=['GET', 'POST'])
@login_required
def caterer_gallery():
    if request.method == 'POST':
        description = request.form.get('desc')
        photos = request.files.getlist('photos')

        if photos:
            image_list = []
            for photo in photos[:4]:
                file_name = photo.filename
                ext = os.path.splitext(file_name)[1] 
                new_filename = token_hex(16) + ext
                photo.save('groovekitchen/static/gallery/' + new_filename)
                image_list.append(new_filename)
           
            images = '*'.join(image_list)
            gal = Gallery(description=description, image=images, catererid=cid)
            db.session.add(gal)
            db.session.commit()
            return jsonify({'status': 'success'})
        else:
            return jsonify({'status': 'error'})
    else:
        cid = session.get('useronline')
        catererid = Caterer.query.get_or_404(cid)
        gallery = Gallery.query.filter_by(catererid=cid).all()
    return render_template('caterers/event_gallery.html', title='My Gallery', gallery=gallery, caterer=catererid)

