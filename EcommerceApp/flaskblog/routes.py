import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort
from flaskblog import app, db, bcrypt
from flaskblog.forms import RegistrationForm, LoginForm, UpdateAccountForm, ProductForm
from flaskblog.models import User, Product, Store
from flask_login import login_user, current_user, logout_user, login_required


@app.route("/")
@app.route("/home")
def home():
    products = Product.query.all()
    return render_template('home.html', products=products)


@app.route("/my_products")
@login_required
def my_products():
    products = Product.query.filter_by(user_id=current_user.id).all()
    return render_template('home.html', products=products)


@app.route("/about")
def about():
    return render_template('about.html', title='About')


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            flash('You logged In successfully, You are now able to your update Data... ', 'success')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    logout_user()
    flash('You logged out successfully', 'info')
    return redirect(url_for('home'))


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_profile = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_profile)
    return render_template('account.html', title='Account',
                           image_file=image_file, form=form)


def save_product_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/product_pics', picture_fn)

    output_size = (250, 250)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


@app.route("/product/new", methods=['GET', 'POST'])
@login_required
def new_product():
    form = ProductForm()
    if form.validate_on_submit():
        store = Store.query.filter_by(name=form.store.data).first()
        if form.picture.data:
            picture_file = save_product_picture(form.picture.data)
            product = Product(title=form.title.data, content=form.content.data, owner=current_user, store=store, type=form.type.data, price=form.price.data, exchangeList=form.exchangeList.data, image_product=picture_file)
        else:
            product = Product(title=form.title.data, content=form.content.data, owner=current_user, store=store, type=form.type.data, price=form.price.data, exchangeList=form.exchangeList.data)
        db.session.add(product)
        db.session.commit()
        flash('Your product announcement has been created!', 'success')
        return redirect(url_for('home'))
    return render_template('create_product.html', title='New Product',
                           form=form, legend='New Product')


@app.route("/product/<int:product_id>")
def product(product_id):
    product = Product.query.get_or_404(product_id)
    image_file = url_for('static', filename='product_pics/' + product.image_product)
    return render_template('product.html', title=product.title, product=product, image_file=image_file)


@app.route("/product/<int:product_id>/update", methods=['GET', 'POST'])
@login_required
def update_product(product_id):
    product = Product.query.get_or_404(product_id)
    if product.owner != current_user:
        abort(403)
    form = ProductForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_product_picture(form.picture.data)
            product.image_product = picture_file
        product.title = form.title.data
        product.content = form.content.data
        product.store = Store.query.filter_by(name=form.store.data).first()
        product.type = form.type.data
        product.price = form.price.data
        product.exchangeList = form.exchangeList.data
        db.session.commit()
        flash('Your product announcement has been updated!', 'success')
        return redirect(url_for('product', product_id=product.id))
    elif request.method == 'GET':
        form.title.data = product.title
        form.content.data = product.content
        form.type.data = product.type
        form.store.data = product.store.name
        form.price.data = product.price
        form.exchangeList.data = product.exchangeList
        form.picture.data = product.image_product
    return render_template('create_product.html', title='Update Product', form=form, legend='Update Product')


@app.route("/product/<int:product_id>/delete", methods=['POST'])
@login_required
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    if product.owner != current_user:
        abort(403)
    db.session.delete(product)
    db.session.commit()
    flash('Your product has been deleted!', 'success')
    return redirect(url_for('home'))
