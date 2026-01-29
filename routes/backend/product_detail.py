from flask import request, redirect, url_for

from app import app, render_template
from model.Product import Product


@app.route("/admin/product-detail")
def product_detail():
    module = 'products'
    # Get the ID from the URL query string (?id=...)
    pro_id = request.args.get('id')

    if not pro_id:
        return redirect(url_for('products'))

    # DATABASE FETCH: Replace this with your actual database query
    # Example: product = db.execute('SELECT * FROM products WHERE id = ?', (pro_id,)).fetchone()
    product = Product.query.get(int(pro_id))

    if not product:
        return "Product not found", 404

    # Pass the 'product' object so your HTML {{ product.name }} etc. works
    return render_template('backend/product_detail.html',
                           active_page='products',
                           module=module,
                           product=product,
                           page_title='Products Detail'
                           )
