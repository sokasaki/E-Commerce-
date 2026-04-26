from app import app, db, render_template, request, redirect, url_for, session, flash, jsonify
from model import CartItem, Product, Order, OrderItem, Customer
import qrcode
import io
import base64
import time
from khqr_service import KHQRService

@app.route('/api/generate_qr', methods=['POST'])
def generate_qr_api():
    user_id = session.get('user_id')
    if not user_id:
        return {"error": "Not logged in"}, 401
        
    cart_items = CartItem.query.filter_by(user_id=user_id).all()
    if not cart_items:
        return {"error": "Cart is empty"}, 400
        
    total = sum(item.product.price * item.quantity for item in cart_items if item.product)
    if total > 0:
        total += 7.00 # $5.00 shipping and $2.00 tax
        
    khqr_service = KHQRService()
    import time
    import uuid
    amount_khr = 100 # Hardcoded for testing
    # Generate a unique bill number using timestamp + random suffix
    bill_number = f"TRX{int(time.time())}-{uuid.uuid4().hex[:6].upper()}"
    
    khqr_data = khqr_service.generate_qr_string(
        bank_account='nol_piseth@bkrt',
        merchant_name='Nol Piseth',
        amount=amount_khr,
        bill_number=bill_number,
        currency='KHR',
        merchant_city='Phnom Penh',
        store_label='MShop',
        phone_number='855884777905',
        terminal_label='Cashier-01'
    )
    qr_string = khqr_data['qr']
    md5 = khqr_data['md5']
    session['bakong_qr_md5'] = md5
    
    qr = qrcode.QRCode(version=None, box_size=10, border=5, error_correction=qrcode.constants.ERROR_CORRECT_L)
    qr.add_data(qr_string)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    qr_base64 = base64.b64encode(buffered.getvalue()).decode()
    
    return {
        "qr_base64": qr_base64,
        "md5": md5
    }

@app.route('/checkout', methods=['GET', 'POST'])
@app.route('/check', methods=['GET', 'POST'])
def check():
    user_id = session.get('user_id')
    if user_id is None:
        flash("Please log in to checkout.", "warning")
        return redirect(url_for('login'))
        
    cart_items = CartItem.query.filter_by(user_id=user_id).all()
    if not cart_items:
        flash("Your cart is empty.", "info")
        return redirect(url_for('cart'))
        
    total = sum(item.product.price * item.quantity for item in cart_items if item.product)
    if total > 0:
        total += 7.00 # Add $5.00 shipping and $2.00 tax to match frontend
    
    # Get customer info if exists
    customer = Customer.query.filter_by(user_id=user_id).first()
    
    if request.method == 'GET':
        session.pop('bakong_qr_md5', None)
    
    if request.method == 'POST':
        payment_method = request.form.get('paymentMethod', 'cod')
        if payment_method == 'bakong':
            payment_verified = request.form.get('payment_verified') == '1'
            payment_md5 = (request.form.get('payment_md5') or '').strip()
            session_md5 = session.get('bakong_qr_md5')

            if not payment_verified or not payment_md5 or payment_md5 != session_md5:
                error_message = "Bakong payment must be verified before placing the order."
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({"status": "error", "error": error_message}), 400
                flash(error_message, "danger")
                return redirect(url_for('check'))

            try:
                verification_result = KHQRService().check_transaction(payment_md5)
                # If API explicitly says not successful, block it
                if str(verification_result.get('responseCode')) != '0':
                    error_message = verification_result.get('message') or "Bakong payment is still pending."
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return jsonify({"status": "error", "error": error_message}), 400
                    flash(error_message, "warning")
                    return redirect(url_for('check'))
            except Exception as exc:
                error_message = f"Unable to verify Bakong payment: {exc}"
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({"status": "error", "error": error_message}), 502
                flash(error_message, "danger")
                return redirect(url_for('check'))

        # If customer doesn't exist, create one from form data
        if not customer:
            customer = Customer(
                user_id=user_id,
                first_name=request.form.get('first_name'),
                last_name=request.form.get('last_name'),
                email=request.form.get('email'),
                phone=request.form.get('phone'),
                address=request.form.get('address'),
                city=request.form.get('city'),
                country=request.form.get('country'),
                zip_code=request.form.get('zip')
            )
            db.session.add(customer)
        else:
            # Update existing customer details
            customer.first_name = request.form.get('first_name')
            customer.last_name = request.form.get('last_name')
            customer.email = request.form.get('email')
            customer.phone = request.form.get('phone')
            customer.address = request.form.get('address')
            customer.city = request.form.get('city')
            customer.country = request.form.get('country')
            customer.zip_code = request.form.get('zip')
        
        # Create new order
        order = Order(
            user_id=user_id,
            total_price=total,
            status='paid' if payment_method == 'bakong' else 'pending'
        )
        db.session.add(order)
        db.session.flush() # Get order ID before committing
        
        # Create order items from cart items
        for item in cart_items:
            order_item = OrderItem(
                order_id=order.id,
                product_id=item.product_id,
                quantity=item.quantity,
                price_at_time=item.product.price
            )
            db.session.add(order_item)
            # Remove from cart
            db.session.delete(item)
            
        db.session.commit()
        session.pop('bakong_qr_md5', None)
        
        # Determine redirection based on payment method
        redirect_url = url_for('order_confirmation', order_id=order.id)
        
        # Real-time notification for admins
        from routes.front.notifications import send_notification_to_all_admins
        send_notification_to_all_admins(
            'New Order!',
            f'Order #{order.id} has been placed by {customer.first_name}. Payment: {payment_method.upper()}',
            'order'
        )
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                "status": "success", 
                "message": "Order placed successfully!", 
                "order_id": order.id, 
                "redirect": redirect_url,
                "payment_method": payment_method
            })

        flash("Order placed successfully!", "success")
        return redirect(redirect_url)
        
    return render_template("front/check-out.html", cart_items=cart_items, total=total, customer=customer)


@app.route('/order-confirmation/<int:order_id>')
def order_confirmation(order_id):
    user_id = session.get('user_id')
    if user_id is None:
        return redirect(url_for('login'))
        
    order = Order.query.filter_by(id=order_id, user_id=user_id).first_or_404()
    return render_template("front/order-confirmation.html", order=order)
