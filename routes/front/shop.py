from app import app, render_template, request, jsonify
from model.Product import Product
from model.Category import Category
import logging

logger = logging.getLogger(__name__)

@app.get('/shop')
def shop():
    query = Product.query
    
    category_filter = request.args.get('category', 'all')
    search_query = request.args.get('search', '')
    
    if category_filter != 'all':
        query = query.join(Category).filter(Category.name.ilike(f'%{category_filter}%'))
    
    if search_query:
        query = query.filter(
            (Product.name.ilike(f'%{search_query}%')) |
            (Product.description.ilike(f'%{search_query}%'))
        )
    
    products = query.all()
    products = [p.to_dict() for p in products]
    
    return render_template("front/shop.html", products=products)

@app.route('/api/products/filter')
def filter_products():
    query = Product.query
    
    category = request.args.get('category', 'all')
    search = request.args.get('search', '')
    sort_by = request.args.get('sort', 'default')
    
    if category != 'all':
        query = query.join(Category).filter(Category.name.ilike(f'%{category}%'))
    
    if search:
        query = query.filter(
            (Product.name.ilike(f'%{search}%')) |
            (Product.description.ilike(f'%{search}%'))
        )
    
    if sort_by == 'price_low':
        query = query.order_by(Product.price.asc())
    elif sort_by == 'price_high':
        query = query.order_by(Product.price.desc())
    
    products = query.all()
    products = [p.to_dict() for p in products]
    
    return jsonify(products)