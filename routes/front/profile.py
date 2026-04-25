from app import app, render_template, session, redirect, url_for, flash
from model import Order, User

@app.get('/profile')
def profile():
    user_id = session.get('user_id')
    if user_id is None:
        flash("Please log in to view your profile.", "warning")
        return redirect(url_for('login'))
        
    user = User.query.get(user_id)
    customer = user.customer_profile if user else None
    # Fetch orders for the logged-in user, ordered by date
    orders = Order.query.filter_by(user_id=user_id).order_by(Order.created_at.desc()).all()
    
    return render_template("front/profile.html", user=user, customer=customer, orders=orders)