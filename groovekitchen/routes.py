import requests, os, random
# import pathlib
from secrets import token_hex
from flask import render_template, request, redirect, url_for, jsonify, session, abort
from sqlalchemy.orm import joinedload
from sqlalchemy import or_
# from google.oauth2 import id_token
# from google_auth_oauthlib.flow import Flow
# from pip._vendor import cachecontrol
# from google.auth.transport.requests import Request
# from google.oauth2.credentials import Credentials
from werkzeug.security import generate_password_hash, check_password_hash
from groovekitchen import app
from groovekitchen.models import db, Product, Cart, Customer, Chef, Caterer, Wishlist, MenuItem, Post, CommunityAgent, Comment, Like, Order, OrderItem, Menu
from groovekitchen.forms import FormData


@app.after_request
def add_no_cache_header(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    return response

@app.template_filter('pluralize')
def pluralize(number, singular='', plural='s'):
    if number == 1:
        return f"{number} {singular}"
    else:
        return f"{number} {plural}"

# app.secret_key = "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"
# os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
# GOOGLE_CLIENT_ID = "996716132297-al93ges5qd3ar6a9r6lc0hb07v2d75l6.apps.googleusercontent.com"
# client_secrets_file = os.path.join(pathlib.Path(__file__).parent, "client_secret.json")
#
# flow = Flow.from_client_secrets_file(
#     client_secrets_file=client_secrets_file,
#     scopes=["openid", "https://www.googleapis.com/auth/userinfo.email", "https://www.googleapis.com/auth/userinfo.profile"],
#     redirect_uri="http://127.0.0.1:5000/callback"
# )

# def refresh_access_token(refresh_token):
#     credentials = Credentials(
#         token=None,
#         refresh_token=refresh_token,
#         client_id=GOOGLE_CLIENT_ID,
#         client_secret=os.path.join(pathlib.Path(__file__).parent, "client_secret.json"),
#         token_uri='https://oauth2.googleapis.com/token'
#     )
#     credentials.refresh(Request())
#     return credentials

# @app.route('/google-login/')
# def google_login():
#     auth_url, customer = flow.authorization_url(prompt='consent')
#     session['customeronline'] = customer
#     return redirect(auth_url)
#
# @app.route('/authorize')
# def authorize():
#     flow.fetch_token(authorization_response=request.url)
#
#     if session['state'] == request.args['state']:
#         abort(500)
    
    # credentials = flow.credentials
    # request_session = requests.session()
    # cached_session = cachecontrol.CacheControl(request_session)
    # token_request = Request(session=cached_session)
    #
    # if credentials.expired:
    #     credentials = refresh_access_token(credentials)
    #     # session['access_token'] = credentials.id_token
    #
    # id_info = id_token.verify_oauth2_token(
    #     id_token=credentials.id_token,
    #     request=token_request,
    #     audience=GOOGLE_CLIENT_ID
    # )
    
    # session['google_id'] = id_info.get('sub')
    # session['name'] = id_info.get('name')
    # session = flow.authorized_session()
    # profile_info = session.get('https://www.googleapis.com/userinfo/v2/me').json()
    # email = profile_info['email']
    # existing_customer = Customer.query.filter_by(email=email).first()
    # if not existing_customer:
    #     try:
    #         customer = Customer(
    #             firstname=profile_info['given_name'],
    #             lastname=profile_info['family_name'],
    #             email=email
    #         )
    #         db.session.add(customer)
    #         db.session.commit()


            # init_session = session.get('customeronline')
            # session['useronline'] = customer.id


    #         session['useronline'] = session.get('customeronline')
    #         session['useronline'] = customer.id
    #         print(session['useronline'])
    #     except Exception as e:
    #         print(e)
    #         return False
    # return redirect(url_for('index'))

@app.route('/', methods=['GET', 'POST'])
def home():
    cid = session.get('useronline')
    menu_items = MenuItem.query.all()
    menu = Menu.query.all() 
    if cid:
        customer = Customer.query.get_or_404(cid)
        number_of_cart_items = Cart.query.filter_by(customerid=customer.id).count() 
    number_of_cart_items = 0
    customer = None
    random.shuffle(menu)
    random.shuffle(menu_items)
    return render_template('index.html',
        title="Home",
        page="home",
        number_of_cart_items=number_of_cart_items,
        menu_items=menu_items,
        menu=menu,
        customer=customer,
    )

@app.route('/index/', methods=['GET', 'POST'])
def index():   
    if session.get('useronline') != None:
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
    return render_template('home.html', title="Home", number_of_cart_items=number_of_cart_items, number_of_wishlist_item=number_of_wishlist_item, customer=customer)

@app.route('/logout/')
def logout():
    session.pop('useronline', None)
    session.clear()
    return redirect(url_for('home'))


@app.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if email and password:
            customer = Customer.query.filter_by(email=email).first()

            if customer:
                chef = Chef.query.filter_by(customerid=customer.id, status='1').first()
                agent = CommunityAgent.query.filter_by(customerid=customer.id, status='1').first()
                caterer = Caterer.query.filter_by(customerid=customer.id, status='1').first()
                if chef:
                    hash_pwd = customer.password
                    check_pwd = check_password_hash(hash_pwd, password)
                    if check_pwd is True:
                        session['useronline'] = customer.id
                        return jsonify({"page": "/chef-dashboard/"})
                    else:
                        return jsonify({"message" : "Password is incorrect.", "status": "incorrect_password"})           
                elif caterer: 
                    hash_pwd = customer.password
                    check_pwd = check_password_hash(hash_pwd, password)
                    if check_pwd is True:
                        session['useronline'] = customer.id
                        return jsonify({"page": "/caterer-dashboard/"})
                    else:
                        return jsonify({"message" : "Password is incorrect.", "status": "incorrect_password"})
                elif agent:
                    hash_pwd = customer.password
                    check_pwd = check_password_hash(hash_pwd, password)
                    if check_pwd is True:
                        session['useronline'] = customer.id
                        return jsonify({"page": "/community-agent-dashboard/"})
                    else:
                        return jsonify({"message" : "Password is incorrect.", "status": "incorrect_password"})  
                else:
                    hash_pwd = customer.password
                    check_pwd = check_password_hash(hash_pwd, password)
                    if check_pwd is True:
                        session['useronline'] = customer.id
                        return jsonify({"page": "/"})
                    else:
                        return jsonify({"message": "Password is incorrect.", "status": "incorrect_password"})  
            else:
                return jsonify({"message": "Email doesn't match any record.", "status": "invalid_email"})
        else:
            return jsonify({"message": "field cannot be empty", "status": "error" })
        form = FormData()
    return render_template('login.html', title='Login', form=form)


# CORS(app)

# locations = []

# @app.route('/locations', methods=['GET'])
# def get_locations():
#     return jsonify(locations)

# @app.route('/location', methods=['POST'])
# def update_location():
#     data = request.get_json()
#     user_id = data['userId']
#     lat = data['lat']
#     lng = data['lng']

#     user_location = next((loc for loc in locations if loc['userId'] == user_id), None)
#     if user_location:
#         user_location['lat'] = lat
#         user_location['lng'] = lng
#     else:
#         locations.append({'userId': user_id, 'lat': lat, 'lng': lng})

#     return jsonify({'message': 'Location updated successfully'})


# @app.route('/map')
# def map():
#     return render_template('map.html')



  # Registration route
@app.route('/registration/', methods=['GET', 'POST'])
def registration():
    if request.method == 'POST':
        firstname = request.form.get('firstname')
        lastname = request.form.get('lastname')
        email = request.form.get('email')
        password = request.form.get('password')
        if firstname and lastname and email and password:
            existing_email = Customer.query.filter(Customer.email == email).first()
            pwd_length = len(password)
            if existing_email is not None:
                return jsonify({"status": "email_taken"})
            elif pwd_length < 8:
                return jsonify({"status": "short_password"})
            else:
                hash_pwd = generate_password_hash(password)
                customer = Customer(
                    firstname=firstname,
                    lastname=lastname,
                    email=email,
                    password=hash_pwd
                )
                db.session.add(customer)
                db.session.commit()
                return jsonify({"page": "/login/"})
        else:
            return jsonify({"status": "error"})
    else:
        form = FormData()
    return render_template('registration.html', form=form, title="Registration")


@app.route('/reactivate-account/', methods=['GET', 'POST'])
def reactivate_account():
    form = FormData()
    if request.method == 'POST':
        email = request.form.get('email')
        
        chef = Chef.query.filter(Chef.email == email).first()
        caterer = Caterer.query.filter(Caterer.email == email).first()
        customer = Customer.query.filter(Customer.email == email).first()

        if chef and chef.status == '2':
            chef.status = '1'
            db.session.commit()
            return jsonify({"status": "success"})
        elif caterer and caterer.status == '2':
            caterer.status = '1'
            db.session.commit()
            return jsonify({"status": "success"})
        elif customer and customer.status == '2':
            customer.status = '1'
            db.session.commit()
            return jsonify({"status": "success"})
        else:
            return jsonify({"status": "error"})
        
    return render_template('reactivate_account.html', title='Reactivate Account', form=form)


@app.route('/password-recovery/', methods=['GET', 'POST'])
def password_recovery():
    form = FormData()
    if request.method == 'POST':
        email = request.form.get('email')
        
        chef = Chef.query.filter(Chef.email == email).first()
        caterer = Caterer.query.filter(Caterer.email == email).first()
        customer = Customer.query.filter(Customer.email == email).first()
        
        password = token_hex(6)

        if chef and chef.status != '0':
            hash_pwd = generate_password_hash(password)
            chef.password = hash_pwd
            db.session.commit()
            return jsonify({"status": "success"})
        elif caterer and caterer.status != '0':
            hash_pwd = generate_password_hash(password)
            chef.password = hash_pwd
            db.session.commit()
            return jsonify({"status": "success"})
        elif customer and customer.status != '0':
            hash_pwd = generate_password_hash(password)
            chef.password = hash_pwd
            db.session.commit()
            return jsonify({"status": "success"})
        else:
            return jsonify({"status": "error"})
        
    return render_template('password_recovery.html', title='Password Recovery', form=form)


@app.route('/fast-orders/', methods=['GET', 'POST'])
def fast_orders():
    if request.method == 'POST':
        order_number = request.form.get('searchInput')
        if order_number:
            order = Order.query.filter_by(order_number=order_number).first()
            if order:
                order_items = OrderItem.query.filter_by(orderid=order.id).all()
                item_list = [{
                    "id": item.productid,
                    "name": item.product_deets.name,
                    "quantity": item.quantity,
                    "price": item.price_per_unit,
                    "orderid": order.id,
                } for item in order_items]
                return jsonify({"status": "success", "item_list": item_list})
            else:
                return jsonify({"status": "not-found"})
        else:
            return jsonify({'status': 'error'})
    else:
        cid = session.get('useronline')
        if cid:
            customer = Customer.query.get_or_404(cid)
            number_of_cart_items = Cart.query.filter_by(customerid=customer.id).count()
        customer = None
        number_of_cart_items = 0
        text = "Enter order Id to load the order items to your cart."
        search = "E.g: GK-OrderId-en5878786fg"
    return render_template('fast_orders.html',
        text=text,
        search=search,
        title='Load Order Items',
        page='fast_orders',
        number_of_cart_items=number_of_cart_items,
        customer=customer
    )


@app.route('/check-order/<string:order_num>/', methods=['POST'])
def check_order(order_num):
    order_number = Order.query.filter_by(order_number=order_num).first()
    if order_number:
        order_items = OrderItem.query.filter_by(orderid=order_number.id).all()
        for item in order_items:
            return load_to_cart(item.orderid)


@app.route('/load-to-cart/<int:id>', methods=['POST'])
def load_to_cart(id):
    cid = session.get('useronline')
    customer = Customer.query.get_or_404(cid) if cid else None
    order_items = OrderItem.query.filter_by(orderid=id).all()

    if order_items:
        cart_items = Cart.query.filter_by(customerid=customer.id).all()
        if cart_items:
            for item in cart_items:
                db.session.delete(item)
                db.session.commit()

        for item in order_items:
            new_cart_item = Cart(customerid=customer.id, productid=item.productid, quantity=item.quantity)
            db.session.add(new_cart_item)
            db.session.commit()

        number_of_cart_items = Cart.query.filter_by(customerid=customer.id).count()
    return jsonify({"status": "success", "number_of_cart_items": number_of_cart_items})


@app.route('/about-us/')
def about_us():
    cid = session.get('useronline')
    if cid:
        customer = Customer.query.get_or_404(cid)
        cart_items = Cart.query.filter_by(customerid=customer.id).count()
    number_of_cart_items = 0
    customer = None
    services = [
        {"name": 'Fast Orders', "logo": 'fa-cart-plus', "description": 'Top notch, bla bla bla bla'},
        {"name": 'Quality Food', "logo": 'fa-utensils', "description": 'Top notch, bla bla bla bla'},
        {"name": 'Master Chefs', "logo": 'fa-user-tie', "description": 'Top notch, bla bla bla bla'},
        {"name": 'Professional Caterers', "logo": 'fa-user', "description": 'Top notch, bla bla bla bla'},
        {"name": 'Top Restaurants', "logo": 'fa-city', "description": 'Top notch, bla bla bla bla'},
        {"name": '24/7 Services', "logo": 'fa-headset', "description": 'Top notch, bla bla bla bla'},]
    testifiers = [
            {"name": 'Mariam Bala', "image": 'testimonial-1.jpg', "occupation": 'Teacher'},
            {"name": 'Moses Ike', "image": 'testimonial-2.jpg', "occupation": 'Software Engineer'},
            {"name": 'Phil Banks', "image": 'testimonial-3.jpg', "occupation": 'Lawyer'},
            {"name": 'Lucinda Kukka', "image": 'testimonial-4.jpg', "occupation": 'Human Resources'},
        ]
    return render_template('about.html',
        title='About Us',
        page='about_us',
        services=services,
        testifiers=testifiers,
        number_of_cart_items=number_of_cart_items,
        customer=customer
    )


@app.route('/get-products/')
def get_products():
    products = Product.query.filter_by(status='1').all()
    if products:
        random.shuffle(products)
        product_list = [{
            "id": product.id,
            "name": product.name,
            "image": product.image,
            "price": product.price,
        } for product in products]
        return jsonify({"status": "success", "product_list": product_list})
    else:
        return jsonify({"status": "not-found"})

@app.route('/top-listing/', methods=['GET', 'POST'])
def top_listings():
    if request.method == 'POST':
        search_input = request.form.get('searchInput')
        if search_input:
            products = Product.query.filter(
                or_(
                    Product.name.ilike(f'%{search_input}%'),
                    Product.price.ilike(f'%{search_input}%'),
                ), Product.status == '1').all()
            if products:
                random.shuffle(products)
                product_list = [{
                    "id": product.id,
                    "name": product.name,
                    "price": product.price,
                    "image": product.image,
                    "onWishlist": product.wishlist_deets,
                } for product in products]

                return jsonify({"status": "success", "product_list": product_list})
            else:
                return jsonify({"status": "not-found"})
        else:
            return jsonify({"status": "error"})
    else:
        text = "Find your favourite meals, protiens, or juices."
        search = "E.g: Korean rice, fruit juice, frilled fish"
        cid = session.get('useronline')
        if cid:
            customer = Customer.query.get_or_404(cid)
            cart_items = Cart.query.filter_by(customerid=customer.id).count()
        number_of_cart_items = 0
        customer = None
    return render_template('top_listings.html',
        text=text,
        search=search,
        title="Top Listing",
        page='top-listing',
        customer=customer,
        number_of_cart_items=number_of_cart_items
    )


@app.route('/product-details/<int:pid>/', methods=['GET', 'POST'])
def product_details(pid):
    cid = session.get('useronline')
    if cid:
        customer = Customer.query.get_or_404(cid)
        number_of_cart_items = Cart.query.filter_by(customerid=customer.id).count()
    number_of_cart_items = 0
    customer = None
    pid = Product.query.filter(Product.id == pid).first()
    products = Product.query.all()
    return render_template('utilities/product_details.html', title='Product Details', product=pid, number_of_cart_items=number_of_cart_items,
                        products=products, customer=customer)


@app.route('/community/', methods=['GET', 'POST'])
def community():
    if session.get('useronline'):
        cid = session.get('useronline')
        customer = Customer.query.get_or_404(cid)
        cart_items = Cart.query.filter_by(customerid=customer.id).all()
        wishlist_items = Wishlist.query.filter_by(customerid=customer.id).all()
        customer_on_list = Like.query.filter_by(customerid=customer.id).first()
        number_of_cart_items = len(cart_items)
        number_of_wishlist_item = len(wishlist_items)
    else:
        number_of_cart_items = 0
        number_of_wishlist_item = 0
        customer = None
        customer_on_list = None
    posts = Post.query.order_by(Post.date_posted.desc()).all()
    comments = Comment.query.all()
    likes = Like.query.all()
    return render_template('community.html', title="Groove Community", page='community', posts=posts, comments=comments, likes=likes, customer_on_list=customer_on_list,
                            customer=customer, number_of_cart_items=number_of_cart_items, number_of_wishlist_item=number_of_wishlist_item)


@app.route('/comments/<int:pid>/')
def get_comments(pid):
    comments = Comment.query.filter_by(postid=pid).order_by(Comment.comment_date).all()
    number_of_comments = len(comments)
    if comments:
        comment_list = [{
            "dp": comment.customer_deets.dp,
            "firstname": comment.customer_deets.firstname,
            "lastname": comment.customer_deets.lastname,
            "content": comment.content,
        } for comment in comments]
        return jsonify({'status': 'success', 'comments': comment_list, 'number_of_comments': number_of_comments})
    else:
        return jsonify({'status': 'error'})


@app.route('/add-comment/', methods=['POST'])
def add_comment():
    new_comment = request.form.get('comment')
    customerid = request.form.get('customerid')
    pid = request.form.get('postid')
    
    if new_comment != '':
        content = Comment(postid=pid, content=new_comment, commenterid=customerid)
        db.session.add(content)
        db.session.commit()
        comments = Comment.query.filter_by(postid=pid).order_by(Comment.comment_date).all()
        number_of_comments = len(comments)
        if comments:
            for comment in comments:
                comment_list = {
                    "dp": comment.customer_deets.dp,
                    "firstname": comment.customer_deets.firstname,
                    "lastname": comment.customer_deets.lastname,
                    "content": comment.content,
                }
            return jsonify({'status': 'success', 'comments': comment_list, 'number_of_comments': number_of_comments})
        else:
            return jsonify({'status': 'error'})
    return jsonify({'status': 'error'})


@app.route('/like-post/', methods=['POST'])
def like_post():
    cid = session.get('useronline')
    customer = Customer.query.get_or_404(cid)

    postid = request.form.get('postId')
    customerid = request.form.get('customerId')

    customer_on_like_list = Like.query.filter_by(customerid=customerid, postid=postid).first()
    post = Post.query.get_or_404(postid)
    if not customer_on_like_list:
        new_like = Like(customerid=customerid, postid=postid)
        db.session.add(new_like)
        post.likes_count += 1 
        customer_on_list = {'customerid': 0}
    else:
        db.session.delete(customer_on_like_list)
        post.likes_count -= 1
        customer_on_list = {'customerid': customer_on_like_list.customerid}
    db.session.commit()
    
    customer_online = {'customer': customer.id} or None
    likes = Like.query.filter_by(postid=postid).all()
    number_of_likes = len(likes)

    return jsonify({"status": "success", "number_of_likes": number_of_likes, 'customer_online': customer_online, 'customer_on_list': customer_on_list})

