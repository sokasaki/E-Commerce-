from flask import request, redirect, url_for, flash, jsonify
from app import app, render_template, db
from model.Order import Order

@app.get('/admin/orders')
def orders():
    status_filter = request.args.get('status')
    search_query = request.args.get('search')
    
    query = Order.query.order_by(Order.created_at.desc())
    
    if status_filter and status_filter != '':
        query = query.filter(Order.status == status_filter)
        
    if search_query:
        # Search by Order ID or customer email/username
        query = query.filter(
            (Order.id.like(f"%{search_query}%")) | 
            (Order.status.like(f"%{search_query}%"))
        )
        
    orders_list = query.all()
    return render_template('backend/orders.html', 
                           active_page='orders',
                           page_title='Orders Management', 
                           orders=orders_list,
                           current_status=status_filter,
                           search_query=search_query)

@app.post('/admin/orders/update_status')
def update_order_status():
    order_id = request.form.get('order_id')
    new_status = request.form.get('status')
    
    order = Order.query.get(order_id)
    if order:
        order.status = new_status
        db.session.commit()
        flash(f"Order #{order_id} status updated to {new_status}.", "success")
    else:
        flash("Order not found.", "danger")
        
    return redirect(url_for('orders'))

@app.get('/admin/orders/<int:order_id>/details')
def get_order_details(order_id):
    order = Order.query.get_or_404(order_id)
    
    items = []
    for item in order.items:
        items.append({
            'product_name': item.product.name if item.product else 'Unknown Product',
            'quantity': item.quantity,
            'price': float(item.price_at_time),
            'subtotal': float(item.price_at_time * item.quantity)
        })

        
    return jsonify({
        'id': order.id,
        'status': order.status,
        'total_price': float(order.total_price),
        'date': order.created_at.strftime('%Y-%m-%d %H:%M'),
        'items': items
    })

@app.get('/admin/orders/<int:order_id>/view')
def admin_order_detail(order_id):
    order = Order.query.get_or_404(order_id)
    # The relationships (user, items, customer_profile) are already linked in the model
    return render_template('backend/order_detail.html', 
                           order=order, 
                           active_page='orders',
                           page_title=f'Order #{order.id}')



