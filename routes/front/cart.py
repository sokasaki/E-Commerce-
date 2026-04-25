from app import app, db, render_template, request, redirect, url_for, session, flash
from model import CartItem, Product
from flask import jsonify

@app.get('/cart')
def cart():
    user_id = session.get('user_id')
    if user_id is None:
        flash("Please log in to view your cart.", "warning")
        return redirect(url_for('login'))
        
    cart_items = CartItem.query.filter_by(user_id=user_id).all()
    total = sum(item.product.price * item.quantity for item in cart_items if item.product)
    
    return render_template("front/cart.html", cart_items=cart_items, total=total)
    
@app.get('/api/cart')
def get_cart_json():
    user_id = session.get('user_id')
    if user_id is None:
        return jsonify([])
        
    cart_items = CartItem.query.filter_by(user_id=user_id).all()
    # Use to_dict from Product model to get full product data including images
    result = []
    for item in cart_items:
        p_dict = item.product.to_dict()
        p_dict['cart_item_id'] = item.id
        p_dict['quantity'] = item.quantity
        result.append(p_dict)
        
    return jsonify(result)

@app.post('/cart/add')
def add_to_cart():
    user_id = session.get('user_id')
    if user_id is None:
        return jsonify({"error": "Login required"}), 401
        
    product_id = request.form.get('product_id', type=int)
    quantity = request.form.get('quantity', 1, type=int)
    
    if not product_id:
        return jsonify({"error": "Product ID required"}), 400
        
    # Check if item already exists in cart
    item = CartItem.query.filter_by(user_id=user_id, product_id=product_id).first()
    
    if item:
        item.quantity += quantity
    else:
        item = CartItem(user_id=user_id, product_id=product_id, quantity=quantity)
        db.session.add(item)
        
    db.session.commit()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({"message": "Item added to cart", "cart_count": CartItem.query.filter_by(user_id=user_id).count()})
        
    flash("Product added to cart!", "success")
    return redirect(url_for('cart'))

@app.post('/cart/update')
def update_cart():
    user_id = session.get('user_id')
    if user_id is None:
        flash("Please log in first.", "warning")
        return redirect(url_for('login'))
        
    item_id = request.form.get('item_id', type=int)
    quantity = request.form.get('quantity', type=int)
    
    if not item_id or quantity is None:
        flash("Invalid request.", "danger")
        return redirect(url_for('cart'))
        
    item = CartItem.query.filter_by(id=item_id, user_id=user_id).first()
    if item:
        if quantity <= 0:
            db.session.delete(item)
            flash("Item removed from cart.", "success")
        else:
            item.quantity = quantity
        db.session.commit()
        
    return redirect(url_for('cart'))


@app.route('/cart/remove/<int:item_id>', methods=['POST', 'GET'])
def remove_from_cart(item_id):
    user_id = session.get('user_id')
    if user_id is None:
        flash("Login required", "danger")
        return redirect(url_for('login'))
        
    item = CartItem.query.filter_by(id=item_id, user_id=user_id).first()
    if item:
        db.session.delete(item)
        db.session.commit()
        flash("Item removed from cart.", "success")
        
    return redirect(url_for('cart'))