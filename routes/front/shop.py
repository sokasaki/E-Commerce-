from app import app, render_template, request, jsonify
from model.Product import Product
from model.Category import Category
import logging

logger = logging.getLogger(__name__)

@app.get('/shop')
def shop():
    try:
        query = Product.query
        
        category_filter = request.args.get('category', 'all')
        search_query = request.args.get('search', '')
        
        if category_filter != 'all':
            query = query.join(Category).filter(Category.name == category_filter)
        
        if search_query:
            query = query.filter(
                (Product.name.ilike(f'%{search_query}%')) |
                (Product.description.ilike(f'%{search_query}%'))
            )
        
        products = query.all()
        products = [p.to_dict() for p in products]
        
        # Get all categories for the filter dropdown
        categories = Category.query.all()
        
        return render_template("front/shop.html", products=products, categories=categories)
    except Exception as e:
        logger.error(f"Error in shop route: {str(e)}")
        return render_template("front/shop.html", products=[], categories=[])

@app.route('/api/products/filter')
def filter_products():
    try:
        query = Product.query
        
        category = request.args.get('category', 'all')
        search = request.args.get('search', '')
        sort_by = request.args.get('sort', 'default')
        
        # Exact category match
        if category != 'all':
            query = query.join(Category).filter(Category.name == category)
        
        # Search filter
        if search:
            query = query.filter(
                (Product.name.ilike(f'%{search}%')) |
                (Product.description.ilike(f'%{search}%'))
            )
        
        # Sorting
        if sort_by == 'price-asc':
            query = query.order_by(Product.price.asc())
        elif sort_by == 'price-desc':
            query = query.order_by(Product.price.desc())
        elif sort_by == 'name-asc':
            query = query.order_by(Product.name.asc())
        elif sort_by == 'name-desc':
            query = query.order_by(Product.name.desc())
        # 'default' - no specific ordering, uses database order
        
        products = query.all()
        products = [p.to_dict() for p in products]
        
        return jsonify(products)
    except Exception as e:
        logger.error(f"Error in filter_products: {str(e)}")
        return jsonify({'error': 'Failed to filter products'}), 500