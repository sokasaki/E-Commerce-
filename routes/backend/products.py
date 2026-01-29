from flask import render_template, request, redirect, url_for
from werkzeug.utils import secure_filename

from app import app, db
from sqlalchemy import text
from sqlalchemy.orm import joinedload
from model.Product import Product
from model.Category import Category
from pathlib import Path
import os
import config
from upload_service import save_image


@app.get('/admin/products')
def products():  # put application's code here
    module = 'products'
    rows = Product.query.options(joinedload(Product.category)).all()
    return render_template('backend/products.html', active_page='products', module=module, products=rows,page_title='Products Management')


@app.get('/admin/products/add')
def add_product_page():
    module = 'products'
    return render_template('backend/add_product.html', active_page='products', module=module, categories=Category.query.all())


@app.post('/admin/products/add')
def add_product():
    file = request.files['image_url']
    filename = None
    if file:
        result = save_image(
            file,
            app.config['UPLOAD_FOLDER'],
            app.config['ALLOWED_EXTENSIONS']
        )
        if isinstance(result, dict):
            filename = result['original']
        else:
            filename = None
            # Optionally handle error: result could be 'no file' or 'invalid file'
            # return f"Image upload error: {result}", 400
    # assert False, file
    try:
        name = request.form.get('name')
        sku = request.form.get('sku')
        price = request.form.get('price')
        stock = request.form.get('stock')
        category_id = request.form.get('category_id')
        description = request.form.get('description')
        image_url = request.form.get('image_url')
        status = request.form.get('status', 'active')

        product = Product(
            name=name,
            sku=sku,
            price=float(price),
            stock=int(stock),
            category_id=int(category_id),
            description=description,
            image_url=filename,
            status=status
        )

        db.session.add(product)
        db.session.commit()
        return redirect(url_for('products'))

    except Exception as e:
        db.session.rollback()
        return f"Error: {str(e)}", 400


@app.get('/admin/products/edit/')
def edit_product_page():
    module = 'products'
    pro_id = request.args.get('id')
    product = Product.query.get(int(pro_id))
    return render_template('backend/edit_product.html', active_page='products', module=module, product=product,
                           categories=Category.query.all())


@app.post('/admin/products/edit/')
def edit_product():
    file = request.files['image_url']
    filename = None
    if file:
        result = save_image(
            file,
            app.config['UPLOAD_FOLDER'],
            app.config['ALLOWED_EXTENSIONS']
        )
        if isinstance(result, dict):
            filename = result['original']
            old_image_name = request.form.get('old_image')
            if old_image_name and old_image_name not in ['no_img.jpg', 'error-img.jpg', '', None]:
                base_dir = Path('static/uploads/products')
                original_path = base_dir / old_image_name
                name, ext = os.path.splitext(old_image_name)
                resized_path = base_dir / f"resized_{name}{ext}"
                thumb_path = base_dir / f"thumb_{name}{ext}"
                for img_path in [original_path, resized_path, thumb_path]:
                    if img_path.is_file():
                        try:
                            img_path.unlink()
                        except Exception as e:
                            print(f"Warning: Could not delete {img_path}: {e}")
        else:
            filename = None
            # Optionally handle error: result could be 'no file' or 'invalid file'
            # return f"Image upload error: {result}", 400

    # assert False, (Path('static/uploads/products') / old_image_name)


    product_id = request.form.get('product_id')
    if product_id is None:
        return "Product ID missing", 400
    try:
        product_id = int(product_id)
    except ValueError:
        return "Invalid Product ID", 400

    name = request.form.get('name')
    sku = request.form.get('sku')
    price = float(request.form.get('price'))
    stock = int(request.form.get('stock'))
    category_id = int(request.form.get('category_id'))
    description = request.form.get('description')
    image_url = filename
    status = request.form.get('status', 'active')

    product = Product.query.get(product_id)
    if not product:
        return "Product not found", 404
    product.name = name
    product.sku = sku
    product.price = price
    product.stock = stock
    product.category_id = category_id
    product.description = description
    if filename:
        product.image_url = image_url
    product.status = status
    db.session.commit()
    return redirect(url_for('products'))


@app.post('/admin/products/delete/')
def delete_product():
    module = 'products'
    pro_id = request.args.get('pro_id')
    product = Product.query.get(pro_id)
    if not product:
        return "Product not found"
    else:
        # Remove image files if not default
        old_image_name = product.image_url
        if old_image_name and old_image_name not in ['no_img.jpg', 'error-img.jpg', '', None]:
            base_dir = Path('static/uploads/products')
            original_path = base_dir / old_image_name
            name, ext = os.path.splitext(old_image_name)
            resized_path = base_dir / f"resized_{name}{ext}"
            thumb_path = base_dir / f"thumb_{name}{ext}"
            for img_path in [original_path, resized_path, thumb_path]:
                if img_path.is_file():
                    try:
                        img_path.unlink()
                    except Exception as e:
                        print(f"Warning: Could not delete {img_path}: {e}")
        db.session.delete(product)
        db.session.commit()
    # assert False,product
    return redirect(url_for('products'))
