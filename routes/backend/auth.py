from flask import request, session, flash, redirect, url_for, render_template
from werkzeug.security import check_password_hash, generate_password_hash
from app import app, db
from model.User import User

@app.get('/login')
def login():
    return render_template('front/login.html')

@app.get('/admin/login')
def admin_login():
    return render_template('backend/login.html')

@app.post('/do_login')
def do_customer_login():
    username = request.form.get('username')
    password = request.form.get('password')
    user = User.query.filter_by(username=username).first()
    
    if user and check_password_hash(user.password, password):
        if user.role != 'customer':
            flash("Please use the admin portal to log in.", "warning")
            return redirect(url_for('admin_login'))
            
        session.clear()
        session['user_id'] = user.id
        session['username'] = user.username
        session['role'] = user.role
        
        # Store full name in session if customer profile exists
        if user.customer_profile:
            session['full_name'] = f"{user.customer_profile.first_name} {user.customer_profile.last_name}"
        else:
            session['full_name'] = user.username
            
        return redirect(url_for('home'))
    
    flash("Invalid username or password.", "danger")
    return redirect(url_for('login'))

@app.post('/do_admin_login')
def do_admin_login():
    username = request.form.get('username')
    password = request.form.get('password')
    user = User.query.filter_by(username=username).first()
    
    if user and check_password_hash(user.password, password):
        if user.role != 'admin':
            flash("Access denied. You do not have admin privileges.", "danger")
            return redirect(url_for('login'))
            
        session.clear()
        session['user_id'] = user.id
        session['username'] = user.username
        session['role'] = user.role
        return redirect(url_for('admin_home'))
    
    flash("Invalid admin credentials.", "danger")
    return redirect(url_for('admin_login'))

@app.get('/register')
def register():
    return render_template('front/register.html')

from model.Customer import Customer

@app.post('/do_register')
def do_register():
    # User Account Info (Email will be used as username)
    email = request.form.get('email')
    password = request.form.get('password')
    confirm_password = request.form.get('confirm_password')
    
    # Customer Profile Info
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    phone = request.form.get('phone')
    
    if not email or not password:
        flash("Email and password are required.", "danger")
        return redirect(url_for('register'))
        
    if password != confirm_password:
        flash("Passwords do not match.", "danger")
        return redirect(url_for('register'))
        
    # Check if email is already in use (either as username or in customer profile)
    if User.query.filter_by(username=email).first() or Customer.query.filter_by(email=email).first():
        flash("This email is already registered.", "danger")
        return redirect(url_for('register'))
        
    try:
        # 1. Create the User record (Email is the username)
        new_user = User(
            username=email,
            password=generate_password_hash(password),
            role='customer'
        )
        db.session.add(new_user)
        db.session.flush() # Get user.id
        
        # 2. Create the Customer record
        new_customer = Customer(
            user_id=new_user.id,
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone
        )
        db.session.add(new_customer)
        db.session.commit()
        
        flash("Registration successful! Please login.", "success")
        return redirect(url_for('login'))
        
    except Exception as e:
        db.session.rollback()
        flash(f"An error occurred: {str(e)}", "danger")
        return redirect(url_for('register'))



@app.get('/logout')
def logout():
    role = session.get('role')
    session.clear()
    flash("You have been logged out.", "info")
    
    if role == 'admin':
        return redirect(url_for('admin_login'))
    return redirect(url_for('home'))