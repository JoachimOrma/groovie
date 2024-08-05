from flask import render_template, request, redirect, url_for, session, jsonify, json
from secrets import token_hex
from groovekitchen import app
from groovekitchen.models import db, Menu, MenuItem, Customer, Cart, Speciality


@app.route('/manage-menu/')
def manage_menu():
    menu_list = Menu.query.all()  
    cid = session.get('useronline')
    if cid:
        customer = Customer.query.get_or_404(cid)
        number_of_cart_items = Cart.query.filter_by(customerid=customer.id).count()
    number_of_cart_items = 0
    customer = None
    return render_template('admin/manage_menu.html',
        customer=customer,
        number_of_cart_items=number_of_cart_items,
        menu_list=menu_list,
    )


@app.route('/create-speciality/', methods=['POST'])
def create_speciality():
    if request.method == 'POST':
        speciality_name = request.form.get('speciality')
        if speciality_name:
            speciality = Speciality(name=speciality_name)
            db.session.add(speciality)
            db.session.commit()
            return jsonify({"status": "success"})
    return jsonify({"status": "error"})


@app.route('/create-menu/', methods=['POST'])
def create_menu():
    if request.method == 'POST':
        menu_name = request.form.get('menuName')
        menu_photo = request.files.get('photo')
        
        if  menu_name and menu_photo:
            file_name = menu_photo.filename
            file_deets = file_name.split('.')
            ext = file_deets[-1]
            new_filename = token_hex(12) + '.' + ext
            menu_photo.save('groovekitchen/static/menu/' + new_filename)
            menu = Menu(name=menu_name, image=new_filename)
            db.session.add(menu)
            db.session.commit()
            return jsonify({"status":"success"})
    return jsonify({"status": "error"})


@app.route('/create-menu-item/', methods=['POST'])
def create_menu_item():
    if request.method == 'POST':
        menu = request.form.get('menu')
        menu_item = request.form.get('menuItem')

        if menu and menu_item:
            new_item = MenuItem(name=menu_item, menuid=menu)
            db.session.add(new_item)
            db.session.commit()
            return jsonify({"status":"success"})
    return jsonify({"status": "error"})


