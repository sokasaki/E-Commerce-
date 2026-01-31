from flask import request

from app import app, render_template, redirect, url_for
from werkzeug.security import check_password_hash
from model.User import User
from flask import session, flash


@app.get('/login')
def login():
    return render_template('backend/login.html')


@app.post('/do_login')
def do_login():
    form = request.form
    username = form.get('username')
    password = form.get('password')
    
    # Default credentials for first-time login (when no users exist in database)
    DEFAULT_USERNAME = "admin"
    DEFAULT_PASSWORD = "admin123"
    
    # Check if user exists in database
    user = User.query.filter_by(username=username).first()
    
    if user:
        # Validate against database user
        if check_password_hash(user.password, password):
            session.clear()
            session['user_id'] = user.id
            session['username'] = user.username
            return redirect(url_for('admin_home'))
        else:
            flash("Invalid password or username")
            return redirect(url_for('login'))
    else:
        # Check against default credentials when no user exists in database
        user_count = User.query.count()
        if user_count == 0 and username == DEFAULT_USERNAME and password == DEFAULT_PASSWORD:
            # Allow login with default credentials
            session.clear()
            session['user_id'] = 0  # Temporary ID for default admin
            session['username'] = DEFAULT_USERNAME
            flash("Logged in with default credentials. Please create a user account immediately!")
            return redirect(url_for('admin_home'))
        
        flash("Invalid password or username")
        return redirect(url_for('login'))


@app.get('/logout')
def logout():
    session.clear()
    return render_template('backend/login.html')