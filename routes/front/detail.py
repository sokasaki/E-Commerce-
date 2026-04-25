from app import app, render_template, request
from model.Product import Product
from model.ProductImage import ProductImage
from urllib.parse import unquote
from flask import url_for
import logging

logger = logging.getLogger(__name__)

@app.get('/detail')
def detail():
    product_name = request.args.get('name') or request.args.get('product-title')
    product = None
    
    if product_name:
        decoded_name = unquote(product_name)
        product = Product.query.filter_by(name=decoded_name, status='active').first()
    
    if not product:
        product_id = request.args.get('id')
        if product_id:
            try:
                product = Product.query.filter_by(id=int(product_id), status='active').first()
            except (ValueError, TypeError):
                pass
    
    if product:
        product_dict = product.to_dict()
        
        # Get all product images
        product_images = ProductImage.query.filter_by(product_id=product.id).order_by(ProductImage.display_order).all()
        
        # Build image URLs list
        images = []
        if product_images:
            for img in product_images:
                if img.image_url:
                    if img.image_url.startswith(('http://', 'https://')):
                        images.append(img.image_url)
                    else:
                        images.append(url_for('static', filename=f'uploads/products/{img.image_url}'))
        elif product.image_url:
            # Fallback to legacy image_url field
            if product.image_url.startswith(('http://', 'https://')):
                images.append(product.image_url)
            else:
                images.append(url_for('static', filename=f'uploads/products/{product.image_url}'))
        
        products = Product.query.filter_by(status='active').limit(4).all()
        products = [p.to_dict() for p in products]
    else:
        product_dict = None
        images = []
        products = []
    
    return render_template("front/product-detail.html", product=product_dict, images=images, products=products)