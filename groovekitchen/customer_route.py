import os, requests, random
from functools import wraps
from secrets import token_hex
from flask import render_template, request, redirect, url_for, flash, session, jsonify ,json
from groovekitchen import app
from groovekitchen.models import db, Customer, Product, Cart, Payment, Order, Wishlist, OrderItem



# A function to clear cache
@app.after_request
def add_no_cache_header(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    return response


# A function to fetch a customer using their id
def get_customer_by_id(cid):
    customer_details = db.session.query(Customer).get_or_404(cid)
    return customer_details


# A decorator that checks if a customer is online
def login_required(func):
    @wraps(func)
    def check_login(*args, **kwargs):
        if session.get('useronline') is not None:
            return func(*args, **kwargs)
        else:
            return redirect(url_for('login.html'))
    return check_login


@app.route('/cart-details/', methods=['GET', 'POST'])
def cart_details():
    cid = session.get('useronline')
    customer = Customer.query.get_or_404(cid)
    products = Product.query.filter(Product.status=='1').all()
    cart_items = Cart.query.filter_by(customerid=customer.id).all()
    wishlist_items = Wishlist.query.filter_by(customerid=customer.id).all()
    product_list = []
    final_total = 0
    
    for item in cart_items:
       product = Product.query.get_or_404(item.productid)
       product.quantity = item.quantity
       final_total = final_total + (product.price * product.quantity)
       product_list.append(product)
    number_of_cart_items = len(cart_items) if cart_items else 0
    number_of_wishlist_item = len(wishlist_items) if wishlist_items else 0
       
    return render_template('utilities/cart_details.html', title="Cart Details", product_list=product_list, final_total=final_total, customer=customer,
                products=products, number_of_wishlist_item=number_of_wishlist_item, number_of_cart_items=number_of_cart_items)
    

@app.route('/clear-cart/')
def clear_cart():
    cid = session.get('useronline')
    customer = Customer.query.get_or_404(cid)
    cart_items = Cart.query.filter_by(customerid=customer.id).all()
    
    for item in cart_items:
        db.session.delete(item)
        db.session.commit()
    return redirect(url_for('cart_details'))

    
@app.route('/add-to-cart/<int:fid>/', methods=['GET','POST'])
def add_to_cart(fid):
    cid = session.get('useronline')
    customer = Customer.query.get_or_404(cid)        
    cart_item = Cart.query.filter_by(productid=fid, customerid=customer.id).first()
    if cart_item:
        cart_item.quantity += 1
    else:
        new_item = Cart(productid=fid, customerid=customer.id)
        db.session.add(new_item)
    db.session.commit()

    cart_items = Cart.query.filter_by(customerid=customer.id).all()
    cart = Cart.query.filter_by(productid=fid).first()
    if cart:
        cart_list = {
            "quantity": cart.quantity,
            "productid": cart.productid,
        }
    number_of_cart_items = len(cart_items) if cart_items else 0
    return jsonify({"status": "success", "number_of_cart_items": number_of_cart_items, "cart_list": cart_list})
        
   
@app.route('/remove-from-cart/<int:fid>/', methods=['GET','POST'])
def remove_from_cart(fid):
    cart_item = Cart.query.filter_by(productid=fid).first()
    if cart_item.quantity == 0:
        db.session.delete(cart_item)
    else:
        cart_item.quantity -= 1
    db.session.commit()
    cart_list = {
        "quantity": cart_item.quantity,
        "productid": cart_item.productid,
    }
    return jsonify({"status": "success", "cart_list": cart_list})

    
@app.route('/delete-item/<int:fid>', methods=['GET', 'POST'])
def delete_item(fid):
    cart_item = Cart.query.filter_by(productid=fid).first()
    db.session.delete(cart_item)     
    db.session.commit()
    return redirect(url_for('cart_details'))


@app.route('/checkout/', methods=['GET', 'POST'])
def checkout():
    cid = session.get('useronline')
    customer = Customer.query.get_or_404(cid)
    if request.method == 'POST':
        firstname = request.form.get('firstname')
        lastname = request.form.get('lastname')
        amount = request.form.get('amount')
        email = request.form.get('email')
        ref = str(token_hex(16))
        session['payref'] = ref
        
        payment = Payment(amount=amount, customerid=customer.id, firstname=firstname, lastname=lastname, status='pending', email=email, ref=ref)
        db.session.add(payment)
        db.session.commit()
    return redirect(url_for('confirm_payment'))


@app.route('/confirm-payemnt/', methods=['GET', 'POST'])
def confirm_payment():
    ref = session.get('payref')
    if ref and session.get('useronline'):
        payment_deets = Payment.query.filter_by(ref=ref).first()
        cid = session.get('useronline')
        customer = Customer.query.get_or_404(cid)
        cart_items = Cart.query.filter_by(customerid=customer.id).all()
        wishlist_items = Wishlist.query.filter_by(customerid=customer.id).all()
        number_of_cart_items = len(cart_items) if cart_items else 0
        number_of_wishlist_item = len(wishlist_items) if wishlist_items else 0

    product_list = []
    final_total = 0
    
    for item in cart_items:
       product = Product.query.get_or_404(item.productid)
       product.quantity = item.quantity
       final_total = final_total + (product.price * product.quantity)
       product_list.append(product)
    return render_template('utilities/confirm_payment.html', title='Confirm Payment', payment_deets=payment_deets, product_list=product_list, number_of_cart_items=number_of_cart_items, customer=customer, number_of_wishlist_item=number_of_wishlist_item)


@app.route('/paystack/initialize/', methods=['GET', 'POST'])
def paystack_initialize():
    ref = session.get('payref')
    if ref:
        payment_deets = Payment.query.filter_by(ref=ref).first()
        amount = payment_deets.amount * 100
        email = payment_deets.email
        callback_url = 'http://127.0.0.1:5000/payment/landing/'
        
        headers = {"ContentType": "application/json",
                   "Authorization": "Bearer sk_test_a2d0c7ea61fb4871d77101b996cc58955eea4e40"}
        url = "https://api.paystack.co/transaction/initialize"
        data = {"email": email, "amount": amount, "reference": ref, "callback_url": callback_url}
        
        try:
            response = requests.post(url, headers=headers,data=json.dumps(data))
            response_json = response.json()
            if response_json and response_json['status'] is True:
                checkoutpage = response_json['data']['authorization_url']
                return redirect(checkoutpage)
            else:
                flash(f"{response_json['message']}", 'error')
                return redirect(url_for('checkout'))
        except:
            flash("We could not connect to paystack", 'error')
            return redirect(url_for('checkout'))


@app.route('/payment/landing/')
def payment_landig_page():
    ref = session.get('payref')
    paystackref = request.args.get('reference')
    if ref == paystackref:
        url = "https://api.paystack.co/transaction/verify/"+ref
        headers = {
            "ContentType": "application/json",
            "Authorization": "Bearer sk_test_a2d0c7ea61fb4871d77101b996cc58955eea4e40"
        }
        response = requests.get(url, headers=headers)
        response_json = response.json()
        payment = Payment.query.filter_by(ref=ref).first()
        
        if response_json and response_json['status'] is True:
            payment.status = 'paid'
            orderid = str(token_hex(16))
            order = Order(order_number=orderid, customerid=payment.customerid, paymentid=payment.id)
            db.session.add(order)
        else:
            payment.status = 'failed'
        db.session.commit()
        return redirect(url_for('payment_status'))
    return redirect('/cart-details/')
    
    
@app.route('/payment-status/', methods=["GET", "POST"])
def payment_status():
    if session.get('useronline'):
        cid = session.get('useronline')
        customer = Customer.query.get_or_404(cid) or None
        cart_items = Cart.query.filter_by(customerid=customer.id).all()
        wishlist_items = Wishlist.query.filter_by(customerid=customer.id).all()
        number_of_cart_items = len(cart_items) if cart_items else 0
        number_of_wishlist_item = len(wishlist_items) if wishlist_items else 0
        ref = session.get('payref')
        payment_deets = Payment.query.filter_by(ref=ref).first()
        order_deets = Order.query.filter_by(paymentid=payment_deets.id).first()

        for item in cart_items:
            product = Product.query.get_or_404(item.productid)
            order_item = OrderItem(orderid=order_deets.id, productid=item.productid, quantity=item.quantity, price_per_unit=product.price)
            db.session.add(order_item)
            db.session.commit()
    
    return render_template('utilities/payment_status.html', title="Payment Status", payment_deets=payment_deets, order_deets=order_deets, customer=customer,
                            number_of_cart_items=number_of_cart_items, number_of_wishlist_item=number_of_wishlist_item)


@app.route('/add-to-wishlist/<int:fid>/', methods=['GET','POST'])
def add_to_wishlist(fid):
    cid = session.get('useronline')
    customer = Customer.query.get_or_404(cid)
    new_item = Wishlist(productid=fid, customerid=customer.id)
    db.session.add(new_item)
    db.session.commit()
    wishlist_items = Wishlist.query.filter_by(customerid=customer.id).all()
    number_of_wishlist_item = len(wishlist_items)
    return jsonify({"status": "success", "message": "Item added to wishlist", "number_of_wishlist_item": number_of_wishlist_item})


@app.route('/remove-from-wishlist/<int:fid>/', methods=['GET','POST'])
def remove_from_wishlist(fid):
    cid = session.get('useronline')
    customer = Customer.query.get_or_404(cid)
    wishlist_item = Wishlist.query.filter_by(productid=fid).first()
    db.session.delete(wishlist_item)  
    db.session.commit()
    wishlist_items = Wishlist.query.filter_by(customerid=customer.id).all()
    number_of_wishlist_item = len(wishlist_items)
    return jsonify({"status": "success", "message": "Item removed from wishlist", "number_of_wishlist_item": number_of_wishlist_item})


@app.route('/wishlist/')
def wishlist():
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
        wishlist_items = None
        customer = None
    return render_template('utilities/wishlist.html', title='My Wishlist', wishlist_items=wishlist_items, number_of_cart_items=number_of_cart_items, customer=customer, number_of_wishlist_item=number_of_wishlist_item)


@app.route('/delete-wishlist/<int:wid>')
def delete_wishlist(wid):
    wishlist_item = Wishlist.query.filter_by(id=wid).first()
    db.session.delete(wishlist_item)     
    db.session.commit()
    return redirect(url_for('wishlist'))


@app.route('/payment-history/')
def payment_history():
    if session.get('useronline'):
        cid = session.get('useronline')
        customer = Customer.query.get_or_404(cid)
        cart_items = Cart.query.filter_by(customerid=customer.id).all()
        wishlist_items = Wishlist.query.filter_by(customerid=customer.id).all()
        number_of_cart_items = len(cart_items)
        number_of_wishlist_item = len(wishlist_items)
        payment_lists = Payment.query.filter_by(customerid=customer.id).order_by(Payment.date_paid).all()
    else:
        number_of_cart_items = 0
        number_of_wishlist_item = 0
        customer = None
    return render_template('utilities/payment_history.html', title='My Payment History', payment_lists=payment_lists, number_of_cart_items=number_of_cart_items,
                            customer=customer, number_of_wishlist_item=number_of_wishlist_item)


@app.route('/order-history/')
def order_history():
    if session.get('useronline'):
        cid = session.get('useronline')
        customer = Customer.query.get_or_404(cid) or None
        cart_items = Cart.query.filter_by(customerid=customer.id).all()
        wishlist_items = Wishlist.query.filter_by(customerid=customer.id).all()
        number_of_cart_items = len(cart_items) if cart_items else 0
        number_of_wishlist_item = len(wishlist_items) if wishlist_items else 0
        order_lists = Order.query.filter_by(customerid=customer.id).order_by(Order.date_ordered).all()
    return render_template('utilities/order_history.html', title='My Order History', order_lists=order_lists, number_of_cart_items=number_of_cart_items,
                            customer=customer, number_of_wishlist_item=number_of_wishlist_item)


@app.route('/remove-orderitem/<int:pid>/<int:oid>/')
def remove_orderitem(pid, oid):
    order_item = OrderItem.query.filter_by(productid=pid).first()
    db.session.delete(order_item)
    db.session.commit()
    order = Order.query.filter_by(id=oid).first()
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
        return jsonify({"status": "error"})


@app.route('/load-items-to-cart/<int:oid>/')
def load_items_to_cart(oid):
    cid = seaaion.get('useronline')
    customer = Customer.query.get(cid)
    order_items = OrderItem.query.filter_by(orderid=oid).all()
    for item in order_items:
        cart = Cart(productid=item.id, quantity=item.quantity, customerid=customer.id)
        db.session.add(cart)
    existing_cart = Cart.query.filter_by(customerid=customer.id).all()
    db.session.delete(existing_cart)
    db.session.commit()
    return redirect(url_for('cart_details'))