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
    user = User.query.filter_by(username=username).first()
    if user:
        if check_password_hash(user.password, password):
            session.clear()
            session['user_id'] = user.id
            session['username'] = user.username
            return redirect(url_for('admin_home'))
        else:
            flash("invalid password or username")
            return redirect(url_for('login'))
    flash("invalid password or username")
    return redirect(url_for('login'))


@app.get('/logout')
def logout():
    session.clear()
    return render_template('backend/login.html')