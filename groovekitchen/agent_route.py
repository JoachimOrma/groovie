import re, os
from secrets import token_hex
from flask import render_template, request, redirect, url_for, flash, session, jsonify, json
from groovekitchen import app
from groovekitchen.models import db, Customer, Cart, Chef, Product, Wishlist, CommunityAgent

@app.route('/restaurants/')
def restaurants():
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
    restaurants = [
        {"name": 'Peaky Blinders', "image": 'restaurant1.jpg', "rating": 4.5},
        {"name": 'House of El', "image": 'restaurant2.jpg', "rating": 4.0},
        {"name": 'Latte Mall', "image": 'restaurant3.jpg', "rating": 4.7},
        {"name": 'Lussade Mart', "image": 'restaurant4.jpg', "rating": 4.9},
        {"name": 'Alexa & Katie', "image": 'restaurant5.jpg', "rating": 5.0},
        {"name": 'Pizza Lounge', "image": 'restaurant6.jpg', "rating": 4.5},
        {"name": 'Despirado Funs', "image": 'restaurant7.jpg', "rating": 4.3},
        {"name": 'Mushin Shin Shin', "image": 'restaurant8.jpg', "rating": 5.0},
        {"name": 'Island of Biu', "image": 'restaurant9.jpg', "rating": 4.6},
    ]
    return render_template('restaurants/restaurant.html', restaurants=restaurants, title='Restaurants', number_of_wishlist_item=number_of_wishlist_item,
                           page='restaurants', number_of_cart_items=number_of_cart_items, customer=customer)

@app.route('/add_product/', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        product_name = request.form.get('product_name')
        product_price = request.form.get('product_price')
        product_desc = request.form.get('product_desc')

        # if product_name and product_desc and product_price:
            # product = Product(product_name=product_name, product_price=product_price, product_description=product_desc)

    return render_template('restaurants/add_product.html')


@app.route('/restaurant-details/')
def restaurant_details():
    if session.get('useronline'):
        cid = session.get('useronline')
        customer = Customer.query.get_or_404(cid)
        cart_items = Cart.query.filter_by(customerid=customer.id).all()
        wishlist_items = Wishlist.query.filter_by(customerid=customer.id).all()
        number_of_cart_items = len(cart_items)
        number_of_wishlist_item = len(wishlist_items)
    else:
        number_of_cart_items = 0
        number_of_wishlist_item = 0
        customer = None

    # restaurantid = .query.filter(Carter.id == cid).first()
    return render_template('restaurants/restaurant_details.html', title='Restaurant Details', number_of_cart_items=number_of_cart_items, customer=customer, number_of_wishlist_item=number_of_wishlist_item)

@app.route('/agents/')
def community_agents():
    agents = CommunityAgent.query.filter_by(status='1').all()
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
    return render_template('agents/agents.html', title='Community Agents', page='community_agent', agents=agents, customer=customer,
                            number_of_wishlist_item=number_of_wishlist_item, number_of_cart_items=number_of_cart_items)

@app.route('/career-as-a-community-agent/')
def community_agent_career():
    cid = session.get('useronline')
    customer = Customer.query.get_or_404(cid) or None
    cart_items = Cart.query.filter_by(customerid=customer.id).all()
    wishlist_items = Wishlist.query.filter_by(customerid=customer.id).all()
    number_of_cart_items = len(cart_items) if cart_items else 0
    number_of_wishlist_item = len(wishlist_items) if wishlist_items else 0

    return render_template('agents/community_agent.html', title="Career as a community agent", customer=customer, number_of_wishlist_item=number_of_wishlist_item, number_of_cart_items=number_of_cart_items)


@app.route('/register-as-a-community-agent/', methods=['GET', 'POST'])
def community_agent_registration():
    if session.get('useronline'):
        cid = session.get('useronline')
        customer = Customer.query.get_or_404(cid)
        cart_items = Cart.query.filter_by(customerid=customer.id).all()
        wishlist_items = Wishlist.query.filter_by(customerid=customer.id).all()
        number_of_cart_items = len(cart_items)
        number_of_wishlist_item = len(wishlist_items)
    else:
        number_of_cart_items = 0
        number_of_wishlist_item = 0
        customer = None
    if request.method == 'POST':
        state = request.form.get('state')
        address = request.form.get('address')
        city = request.form.get('city')
        phone = request.form.get('phone')
        specialities = request.form.get('specialities')
        photo_file = request.files['photo']

        if photo_file and specialities and phone and city and state and address:
            file_name = photo_file.filename
            file_deets = file_name.split('.')
            ext = file_deets[-1]
            new_filename = token_hex(12) + '.' + ext
            photo_file.save('groovekitchen/static/photos/' + new_filename)

            agent = CommunityAgent(
                customerid=customer.id,
                phone=phone,
                state=state,
                city=city,
                status='1',
                specialities=specialities,
                address=address,
            )
            customer.dp=new_filename
            customer.customer_type='agent'
            db.session.add(agent)
            db.session.commit()
            session['agentonline'] = customer.id
            return jsonify({"status": "success"})
        else:
            return jsonify({"status": "error"})

    return render_template('agents/community_agent_registration.html', title="Register as a community agent", customer=customer,
                        number_of_cart_items=number_of_cart_items, number_of_wishlist_item=number_of_wishlist_item)


@app.route('/community-agent-create-product/', methods=['GET', 'POST'])
def community_agent_create_product():
    cid = session.get('useronline')
    agentid = CommunityAgent.query.filter_by(customerid=cid).first()
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
    return render_template('agents/create_product.html', title="Create Product", agent=agentid)


@app.route('/community-agent-dashboard/')
def community_agent_dashboard():
    vid = session.get('useronline')
    agentid = CommunityAgent.query.filter_by(customerid=vid).first()
    return render_template('agents/dashboard.html', title="Community Agent", agent=agentid)


@app.route('/community-agent-profile-setting/', methods=['GET', 'POST'])
def community_agent_profile_setting():
    cid = session.get('useronline')
    agentid = CommunityAgent.query.filter_by(customerid=cid).first()
    customer = Customer.query.filter_by(id=agentid.customerid).first()
    if request.method == 'POST':
        firstname = request.form.get('firstname')
        lastname = request.form.get('lastname')
        state = request.form.get('state')
        city = request.form.get('city')
        email = request.form.get('email')
        address = request.form.get('address')
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

            agentid.state = state
            agentid.city = city
            agentid.phone = phone
            agentid.address = address
            agentid.specialities = specialities
            agentid.working_days = working_days
            customer.dp = new_filename
            customer.lastname = lastname
            customer.firstname = firstname
            customer.email = email

            db.session.commit()
            return jsonify({"page": "/agent-profile-setting/", "status": "success"})
        else:
            return jsonify({"message":"Please complete all data fields!", "status": "error"})

    return render_template('agents/profile_setting.html', title="Profile Setting", agent=agentid)


@app.route('/community-agent-logout/')
# @login_required
def community_agent_logout():
    if session.get('useronline'):
        session.pop('useronline')
        session.clear()
    return redirect(url_for('login'))

@app.route('/community-agent-profile/')
# @login_required
def community_agent_profile():
    cid = session.get('useronline')
    agentid = CommunityAgent.query.filter_by(customerid=cid).first()
    products = Product.query.filter_by(customerid=cid, status='1').all()
    number_of_products = len(products) if products else 0
    return render_template('agents/profile.html', title='My Profile', agent=agentid, number_of_products=number_of_products, products=products)


@app.route('/community-agent-account-setting/')
def community_agent_account_setting():
    vid = session.get('useronline')
    customer = Customer.query.get_or_404(vid)
    agentid = CommunityAgent.query.filter_by(customerid=vid).first()

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
        else:
            return jsonify({"status": "error"})
    return render_template('agents/account_setting.html', title="Account Setting", agent=agentid)


@app.route('/category/<searchInput>/', methods=['GET', 'POST'])
def categories(searchInput):
    if session.get('useronline'):
        cid = session.get('useronline')
        customer = Customer.query.get_or_404(cid)
        cart_items = Cart.query.filter_by(customerid=customer.id).all()
        wishlist_items = Wishlist.query.filter_by(customerid=customer.id).all()
        number_of_cart_items = len(cart_items) if cart_items else 0
        number_of_wishlist_item = len(wishlist_items) if wishlist_items else 0
    else:
        number_of_wishlist_item = 0
        number_of_cart_items = 0
        customer = None
        cart_items = None

    return render_template('agents/categories.html', title="Search result", customer=customer, searchInput=searchInput, number_of_wishlist_item=number_of_wishlist_item, number_of_cart_items=number_of_cart_items)


@app.route('/search-result/', methods=['POST'])
def search_result():
    search_input = request.form.get('searchInput')
    if search_input:
        products = Product.query.filter(Product.name.ilike(f'%{search_input}%')).all()
        if products:
            product_list = [{
                "id": product.id,
                "name": product.name,
                "image": product.image,
                "price": product.price,
                "description": product.description,
                "customerid": product.customerid,
            } for product in products]
            return jsonify({"status": "success", "product_list": product_list})
        else:
            return jsonify({"status": "not-found"})
    else:
        return jsonify({"status": "error"})


@app.route('/community-agent-product/')
def community_agent_product():
    cid = session.get('useronline')
    agentid = CommunityAgent.query.filter_by(customerid=cid).first()
    products = Product.query.filter_by(customerid=cid, status='1').all()
    return render_template('agents/products.html', title="My Products", agent=agentid, products=products)

