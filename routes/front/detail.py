from app import app, render_template, request
from model.Product import Product
from urllib.parse import unquote
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
        product = product.to_dict()
        products = Product.query.filter_by(status='active').limit(4).all()
        products = [p.to_dict() for p in products]
    else:
        products = []
    
    return render_template("front/product-detail.html", product=product, products=products)