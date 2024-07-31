from functools import wraps
import os, re, random
from moviepy.editor import VideoFileClip
from flask import render_template, request, redirect, url_for, session, jsonify
from secrets import compare_digest, token_hex
from werkzeug.security import generate_password_hash
from sqlalchemy import or_
from sqlalchemy.orm import joinedload
from groovekitchen import app
from groovekitchen.forms import FormData
from groovekitchen.models import db, Product, Chef, Cart, Wishlist, Customer, Post, Like, Comment, Booking


ALLOWED_EXTENSIONS_IMAGES = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'jpg', 'jfif'}
ALLOWED_EXTENSIONS_VIDEOS = {'mp4', 'mov', 'avi', 'mkv'}


def get_video_duration(file_path):
    try:
        clip = VideoFileClip(file_path)
        duration = clip.duration
        return duration
    except Exception as e:
        return f"Error: {str(e)}"


def login_required(func):
    @wraps(func)
    def check_login(*args, **kwargs):
        if session.get('useronline') is not None:
            return func(*args, **kwargs)
        else:
            return redirect(url_for('login'))
    return check_login


@app.route('/career-as-a-chef/')
def chef_career():
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
    return render_template('chefs/private_chef.html', title="Career as a professional chef", customer=customer, number_of_cart_items=number_of_cart_items, number_of_wishlist_item=number_of_wishlist_item)


@app.route('/register-as-a-chef/', methods=['GET', 'POST'])
def chef_registration():
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
    if request.method == 'POST':
        state = request.form.get('state')
        city = request.form.get('city')
        phone = request.form.get('phone')
        specialities = request.form.get('specialities')
        working_days = request.form.get('working_days')
        photo_file = request.files['photo']
        
        if state and city and phone and specialities and working_days and photo_file:
            file_name = photo_file.filename
            file_deets = file_name.split('.')
            ext = file_deets[-1]
            new_filename = token_hex(12) + '.' + ext
            photo_file.save('groovekitchen/static/photos/' + new_filename)
            
            chef = Chef(
                customerid=customer.id,
                phone=phone,
                state=state,
                city=city,
                status='1',
                specialities=specialities,
                working_days=working_days,
            )
            customer.dp=new_filename
            customer.customer_type='chef'
            
            db.session.add(chef)
            db.session.commit()
            session['useronline'] = customer.id
            return jsonify({"status": "success"})
        else:
            return jsonify({"status": "error"})
        
    return render_template('chefs/chef_registration.html', title="Register as a professional chef", customer=customer, number_of_cart_items=number_of_cart_items, number_of_wishlist_item=number_of_wishlist_item)


@app.route('/get-chefs/')
def get_chefs():
    chefs = Chef.query.filter_by(status='1', verification='unverified').all()
    if chefs:
        random.shuffle(chefs)
        chef_list = [{
            "id": chef.id,
            "customerid": chef.customerid,
            "firstname": chef.customer_deets.firstname,
            "lastname": chef.customer_deets.lastname,
            "dp": chef.customer_deets.dp,
            "specialities": chef.specialities,
            "city": chef.city,
            "state": chef.state,
        } for chef in chefs]
        return jsonify({"status": "success", "chef_list": chef_list})
    else:
        return jsonify({"status": "not-found"})


@app.route('/chefs/', methods=['GET', 'POST'])
def professional_chefs():
    if request.method == 'POST':
        search_input = request.form.get('searchInput')
        if search_input:
            random.shuffle(chefs)
            chefs = Chef.query.join(Customer).filter(
                or_(
                    Customer.firstname.ilike(f'%{search_input}%'),
                    Customer.lastname.ilike(f'%{search_input}%'),
                    Chef.city.ilike(f'%{search_input}%'),
                    Chef.state.ilike(f'%{search_input}%'),
                    Chef.specialities.ilike(f'%{search_input}%')
                ), Chef.status == '1', Chef.verification == 'unverified').all()
            if chefs:
                chef_list = [{
                    "id": chef.id,
                    "firstname": chef.customer_deets.firstname,
                    "lastname": chef.customer_deets.lastname,
                    "dp": chef.customer_deets.dp,
                    "specialities": chef.specialities,
                    "city": chef.city,
                    "state": chef.state,
                } for chef in chefs]

                return jsonify({"status": "success", "chef_list": chef_list})
            else:
                return jsonify({"status": "not-found"})
        else:
            return jsonify({"status": "error"})
    else:
        if session.get('useronline'):
            cid = session.get('useronline')
            customer = Customer.query.get_or_404(cid)
            cart_items = Cart.query.filter_by(customerid=customer.id).all()
            wishlist_items = Wishlist.query.filter_by(customerid=customer.id).all()
            number_of_wishlist_item = len(wishlist_items)
            number_of_cart_items = len(cart_items)
        else:
            number_of_wishlist_item = 0
            number_of_cart_items = 0
            customer = None
    return render_template('chefs/all_chefs.html',  title='Chefs', page='professional_chef', customer=customer,
                           number_of_cart_items=number_of_cart_items, number_of_wishlist_item=number_of_wishlist_item)


@app.route('/chef-details/<int:cid>/', methods=['GET', 'POST'])
def chef_details(cid):
    chefid = Chef.query.filter(Chef.id == cid).first()
    chefs = Chef.query.filter_by(status='1').all()
    if session.get('useronline'):
        cid = session.get('useronline')
        customer = Customer.query.get(cid)
        cart_items = Cart.query.filter_by(customerid=customer.id).all()
        number_of_cart_items = len(cart_items)
        wishlist_items = Wishlist.query.filter_by(customerid=customer.id).all()
        number_of_wishlist_item = len(wishlist_items)
    else:
        number_of_cart_items = 0
        number_of_wishlist_item = 0
        customer = None
    if request.method == 'POST':
        name = request.form.get('fullname')
        email = request.form.get('email')
        date = request.form.get('datetime')
        address = request.form.get('address')
        message = request.form.get('message')
        
        if name and date and email and address and message:
            booking_deets = Booking(name=name, email=email, date=date, address=address, message=message, booker=customer.id, chef=chefid.id)
            db.session.add(booking_deets)
            db.session.commit()
            return jsonify({"status": "success"})
        else:
            return jsonify({"status": "error"})


    return render_template('chefs/chef_details.html', title='Chef Details', chef=chefid, chefs=chefs, customer=customer, number_of_cart_items=number_of_cart_items, number_of_wishlist_item=number_of_wishlist_item)


@app.route('/chef-dashboard/')
# @login_required
def chef_dashboard():
    cid = session.get('useronline')
    chefid = Chef.query.filter_by(customerid=cid).first()
    bookings = Booking.query.filter_by(chef=chefid.id).all() or None
    total_bookings = len(bookings) if bookings else 0
    
    return render_template('chefs/dashboard.html', title='Dashboard', page="dashboard", chef=chefid, bookings=bookings, total_bookings=total_bookings)


@app.route('/chef-profile/')
@login_required
def chef_profile():
    cid = session.get('useronline')
    chefid = Chef.query.filter_by(customerid=cid).first()
    posts = Post.query.filter_by(posterid=chefid.customerid).all()
    products = Product.query.filter_by(customerid=cid, status='1').all()
    number_of_posts = len(posts) if posts else 0
    number_of_products = len(products) if products else 0
    
    return render_template('chefs/profile.html', title='My Profile', page="chef-profile", chef=chefid, posts=posts, products=products, number_of_posts=number_of_posts, number_of_products=number_of_products)


@app.route('/chef-profile-setting/', methods=['GET', 'POST'])
@login_required
def chef_profile_setting():
    cid = session.get('useronline')
    chefid = Chef.query.filter_by(customerid=cid).first()
    customer = Customer.query.filter_by(id=chefid.customerid).first()
    if request.method == 'POST':
        firstname = request.form.get('firstname')
        lastname = request.form.get('lastname')
        state = request.form.get('state')
        city = request.form.get('city')
        email = request.form.get('email')
        phone = request.form.get('phone')
        specialities = request.form.get('specialities')
        working_days = request.form.get('working_days')
        photo_file = request.files['photo']
        
        if firstname and lastname and state and city and email and phone and specialities and working_days:
            if photo_file:
                file_name = photo_file.filename
                file_deets = file_name.split('.')
                ext = file_deets[-1]
                new_filename = token_hex(16) + '.' + ext
                photo_file.save('groovekitchen/static/photos/' + new_filename)
            else:
                new_filename = customer.dp

            chefid.state = state
            chefid.city = city
            chefid.phone = phone
            chefid.specialities = specialities
            chefid.working_days = working_days
            customer.dp = new_filename
            customer.lastname = lastname
            customer.firstname = firstname
            customer.email = email
            
            db.session.commit()
            return jsonify({"page": "/chef-profile-setting/", "status": "success"})
        else:
            return jsonify({"message":"Please complete all data fields!", "status": "error"})
    
    return render_template('chefs/profile_setting.html', title='Profile Setting', page='profile-setting', chef=chefid)


@app.route('/chef-account-setting/', methods=['GET', 'POST'])
@login_required
def chef_account_setting():
    cid = session.get('useronline')
    chefid = Chef.query.filter_by(customerid=cid).first()
    customer = Customer.query.filter_by(id=chefid.customerid).first()

    if request.method == 'POST':
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        print(request.form)
        if password and confirm_password:
            if compare_digest(password, confirm_password) is True:
                hash_pwd = generate_password_hash(password)
                customer.password=hash_pwd
                db.session.commit()
                return jsonify({"status": "success"})
            else:
                return jsonify({"status": "unmatch_password"}) 
        return jsonify({"status": "error"}) 
    return render_template('chefs/account_setting.html', title='Account Setting', page='account-setting', chef=chefid)


@app.route('/chef-create-product/', methods=['GET', 'POST'])
@login_required
def chef_create_product():
    cid = session.get('useronline')
    chefid = Chef.query.filter_by(customerid=cid).first()
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
    return render_template('chefs/create_product.html', title='Create Product', chef=chefid)


@app.route('/chef-delete-account/<int:cid>/')
@login_required
def chef_delete_account(cid):
    cid = session.get('useronline')
    chefid = Chef.query.filter_by(customerid=cid).first()
    
    chefid.status = '0'
    db.session.commit()
    
    return jsonify({"status": "delete"})


@app.route('/chef-deactivate-account/<int:cid>/')
@login_required
def chef_deactivate_account(cid):
    cid = session.get('useronline')
    chefid = Chef.query.filter_by(customerid=cid).first()
    
    chefid.status = '2'
    db.session.commit()
    
    return jsonify({"status": "deactivate"})


@app.route('/chef-logout/')
@login_required
def chef_logout():
    if session.get('useronline'):
        session.pop('useronline')
        session.clear()
    return redirect(url_for('login'))
    
    
@app.route('/view-chef-profile/')
@login_required
def view_chef_profile():
    cid = session.get('useronline')
    chefid = Chef.query.filter_by(customerid=cid).first()
    return render_template("chefs/view_chef_profile.html", title="View Profile", chef=chefid)


@app.route('/chef-make-post/', methods=['GET', 'POST'])
@login_required
def chef_make_post():
    cid = session.get('useronline')
    chefid = Chef.query.filter_by(customerid=cid).first()
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        file = request.files['mediaFile']
        if file and title and content:
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
                return jsonify({"message": "File type is not allowed.", "status": "not-allowed"})

            post = Post(title=title, content=content, file_type=file_type, category='chef', file=new_filename, posterid=chefid.customerid)
            db.session.add(post)
            db.session.commit()
            return jsonify({"status": "success"})
        return jsonify({"status": "error"})
    return render_template("chefs/chef_make_post.html", title="Social Fields", chef=chefid)


@app.route('/chef-timeline/')
def chef_timeline():
    cid = session.get('useronline')
    chefid = Chef.query.filter_by(customerid=cid).first()
    likes = Like.query.all()
    customer_on_list = Like.query.filter_by(customerid=chefid.id).first()
    posts = Post.query.filter_by(posterid=chefid.customerid).order_by(Post.date_posted.desc()).all() or None
    comments = Comment.query.all()
    return render_template('chefs/timeline.html', title='Timeline', chef=chefid, posts=posts, customer_on_list=customer_on_list, comments=comments, likes=likes)


@app.route('/chef-product/')
def chef_product():
    cid = session.get('useronline')
    chefid = Chef.query.filter_by(customerid=cid).first()
    products = Product.query.filter_by(customerid=cid, status='1').all()
    return render_template('chefs/products.html', title="My Products", chef=chefid, products=products)


@app.route('/chef-delete-product/<int:pid>/')
def chef_delete_product(pid):
    productid = Product.query.get_or_404(pid)
    productid.status='0'
    db.session.commit()
    return redirect(url_for('chef_product'))


@app.route('/chef-view-count/<int:id>/', methods=['GET', 'POST'])
def chef_profile_view_count(id):
    chef = Chef.query.get_or_404(id)
    chef.view_count += 1
    db.session.commit()
    return jsonify({"status": "success"})

