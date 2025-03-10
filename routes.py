import os
from flask import Blueprint, request, render_template, redirect, url_for, flash
from flask_login import login_required, current_user, logout_user
from werkzeug.utils import secure_filename
from models import db, Product

# flask blueprint for handling product-related routes
product_routes = Blueprint('product_routes', __name__)

# allowed file types for image uploads
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# ensures the uploads folder exists to store product images
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# function to check allowed file types for image uploads
def allowed_file(filename):
    """Check if the file extension is allowed (png, jpg, jpeg, gif)."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# renders add product page (only for logged-in admins)
@product_routes.route('/product/add/page', methods=['GET'])
@login_required  
def add_product_page():
    """Displays the form to add a new product."""
    return render_template('add_product.html')

# adding a new product
@product_routes.route('/product/add', methods=['POST'])
@login_required
def add_product():
    """Processes the form submission for adding a new product."""
    name = request.form.get('name')
    category = request.form.get('category')
    price = request.form.get('price')
    description = request.form.get('description')
    image = request.files.get('image')

    # ensures required fields are filled
    if not name or not category or not price:
        flash("Missing required fields: name, category, or price", "error")
        return redirect(url_for('product_routes.add_product_page'))

    # handles image upload 
    image_filename = None
    if image and allowed_file(image.filename):
        filename = secure_filename(image.filename)  
        image.save(os.path.join(UPLOAD_FOLDER, filename))  
        image_filename = filename  

    # saves product to database
    new_product = Product(
        name=name,
        category=category,
        price=float(price),
        description=description,
        image_filename=image_filename
    )
    db.session.add(new_product)
    db.session.commit()
    
    flash("Product added successfully!", "success")
    return redirect(url_for('product_routes.show_products_page'))

# render product list page 
@product_routes.route('/products/page', methods=['GET'])
def show_products_page():
    """Displays all products and allows searching by name."""
    search_query = request.args.get('search', '')

    if search_query:
        products = Product.query.filter(Product.name.ilike(f"%{search_query}%")).all()
    else:
        products = Product.query.all()

    return render_template('products.html', products=products, search_query=search_query)

# render edit product page
@product_routes.route('/product/edit/<int:product_id>', methods=['GET'])
@login_required
def edit_product_page(product_id):
    """Displays the edit form for an existing product."""
    product = db.session.get(Product, product_id)
    if not product:
        flash("Product not found", "error")
        return redirect(url_for('product_routes.show_products_page'))
    
    return render_template('edit_product.html', product=product)

# handle product updates 
@product_routes.route('/product/update/<int:product_id>', methods=['POST'])
@login_required
def update_product(product_id):
    """Processes the form submission to update a product."""
    product = db.session.get(Product, product_id)
    if not product:
        flash("Product not found", "error")
        return redirect(url_for('product_routes.show_products_page'))

    # update product details with new values or keep old ones
    product.name = request.form.get('name', product.name)
    product.category = request.form.get('category', product.category)
    product.price = float(request.form.get('price', product.price))
    product.description = request.form.get('description', product.description)

    # image Update 
    image = request.files.get('image')
    if image and allowed_file(image.filename):
        filename = secure_filename(image.filename)
        image.save(os.path.join(UPLOAD_FOLDER, filename))

        # remove old image if it exists
        if product.image_filename:
            old_image_path = os.path.join(UPLOAD_FOLDER, product.image_filename)
            if os.path.exists(old_image_path):
                os.remove(old_image_path)

        product.image_filename = filename  

    db.session.commit()
    flash("Product updated successfully!", "success")
    return redirect(url_for('product_routes.show_products_page'))

# handle product deletion
@product_routes.route('/product/delete/<int:product_id>', methods=['POST'])
@login_required
def delete_product(product_id):
    """Deletes a product from the database."""
    product = db.session.get(Product, product_id)
    if not product:
        flash("Product not found", "error")
        return redirect(url_for('product_routes.show_products_page'))

    # delete product image from storage if it exists
    if product.image_filename:
        image_path = os.path.join(UPLOAD_FOLDER, product.image_filename)
        if os.path.exists(image_path):
            os.remove(image_path)

    db.session.delete(product)
    db.session.commit()
    flash("Product deleted successfully!", "success")
    return redirect(url_for('product_routes.show_products_page'))

# admin dashboard route (needs to be logged in)
@product_routes.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    """Displays the admin dashboard with product management options."""
    products = Product.query.all()
    return render_template('dashboard.html', products=products, user=current_user)

# logout route
@product_routes.route('/logout')
@login_required
def logout():
    """Logs out the user and redirects to the homepage."""
    logout_user()
    flash("You have been logged out.", "success")
    return redirect(url_for('home'))
