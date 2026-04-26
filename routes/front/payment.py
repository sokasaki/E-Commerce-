from app import app, db, render_template, request, redirect, url_for, session, flash, jsonify
from model import Order
from khqr_service import KHQRService
import qrcode
import io
import base64

khqr_service = KHQRService()

@app.route('/payment/<int:order_id>')
def payment(order_id):
    user_id = session.get('user_id')
    if user_id is None:
        return redirect(url_for('login'))
        
    order = Order.query.filter_by(id=order_id, user_id=user_id).first_or_404()
    
    # User's specific Bakong parameters
    BANK_ACCOUNT = 'nol_piseth@bkrt'
    MERCHANT_NAME = 'Nol Piseth'
    MERCHANT_CITY = 'Phnom Penh'
    CURRENCY = 'KHR'
    STORE_LABEL = 'MShop'
    PHONE_NUMBER = '855884777905'
    TERMINAL_LABEL = 'Cashier-01'
    
    import time
    import uuid
    # Generate a unique bill number using timestamp + random suffix
    bill_number = f"TRX{int(time.time())}-{uuid.uuid4().hex[:6].upper()}"
    
    # conversion rate
    amount_khr = order.total_price * 4100 
    
    khqr_data = khqr_service.generate_qr_string(
        bank_account=BANK_ACCOUNT,
        merchant_name=MERCHANT_NAME,
        amount=amount_khr,
        bill_number=bill_number,
        currency=CURRENCY,
        merchant_city=MERCHANT_CITY,
        store_label=STORE_LABEL,
        phone_number=PHONE_NUMBER,
        terminal_label=TERMINAL_LABEL
    )
    
    qr_string = khqr_data['qr']
    md5 = khqr_data['md5']
    
    # Generate QR Code image as base64
    qr = qrcode.QRCode(version=None, box_size=10, border=5, error_correction=qrcode.constants.ERROR_CORRECT_L)
    qr.add_data(qr_string)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    qr_base64 = base64.b64encode(buffered.getvalue()).decode()
    
    return render_template("front/payment.html", order=order, qr_base64=qr_base64, qr_string=qr_string, md5=md5)

@app.post('/check-payment')
def check_payment():
    json_data = request.get_json(silent=True) or {}
    md5 = (json_data.get('md5') or '').strip()
    if not md5:
        return jsonify({"responseCode": 1, "message": "Missing md5"}), 400

    try:
        return jsonify(khqr_service.check_transaction(md5))
    except Exception as exc:
        return jsonify({"responseCode": 1, "message": str(exc)}), 502

@app.route('/payment/confirm/<int:order_id>', methods=['POST'])
def confirm_payment(order_id):
    user_id = session.get('user_id')
    if user_id is None:
        return redirect(url_for('login'))

    order = Order.query.filter_by(id=order_id, user_id=user_id).first_or_404()

    if order.status == 'paid':
        message = "Payment already confirmed."
        if request.is_json:
            return jsonify({"status": "success", "message": message})
        flash(message, "success")
        return redirect(url_for('order_confirmation', order_id=order.id))

    payload = request.get_json(silent=True) if request.is_json else request.form
    md5 = (payload.get('md5') or '').strip() if payload else ''
    if not md5:
        message = "Payment reference is missing."
        if request.is_json:
            return jsonify({"status": "error", "message": message}), 400
        flash(message, "danger")
        return redirect(url_for('payment', order_id=order.id))

    try:
        result = khqr_service.check_transaction(md5)
    except Exception as exc:
        message = f"Unable to verify payment: {exc}"
        if request.is_json:
            return jsonify({"status": "error", "message": message}), 502
        flash(message, "danger")
        return redirect(url_for('payment', order_id=order.id))

    if str(result.get('responseCode')) != '0':
        message = result.get('message') or "Payment has not been confirmed yet."
        if request.is_json:
            return jsonify({"status": "error", "message": message, "result": result}), 400
        flash(message, "warning")
        return redirect(url_for('payment', order_id=order.id))

    order.status = 'paid'
    db.session.commit()

    message = "Payment confirmed successfully."
    if request.is_json:
        return jsonify({"status": "success", "message": message})
    flash(message, "success")
    return redirect(url_for('order_confirmation', order_id=order.id))
