from app import app, render_template
from app import db
from sqlalchemy import text
from flask import request, redirect, url_for,flash
from werkzeug.security import generate_password_hash
from model.User import User


@app.get('/admin/users')
def users():
    module = 'users'
    rows = User.query.all()  # now returns ORM objects
    return render_template('backend/users.html', active_page='users', module=module, users=rows,page_title='Users Management')


# @app.route("/raw_users")
# def raw_users():
#     sql = text("SELECT * FROM user")
#     result = db.session.execute(sql)
#     rows = [dict(row._mapping) for row in result]
#     return {"users": rows}
#

@app.get('/admin/addUser')
def addUser_page():  # put application's code here
    return render_template('backend/User/addUser.html', active_page='addUser')


@app.post('/admin/addUser')
def addUser():  # put application's code here
    username = request.form["username"]
    password = request.form["password"]
    hashed_password = generate_password_hash(password)
    user = User(
        username=username,
        password=hashed_password
    )
    db.session.add(user)
    db.session.commit()

    return redirect(url_for('users'))


@app.get('/admin/editUser')
def editUser_page():  # put application's code here
    module = 'users'
    user_id = request.args.get('user_id')
    user = User.query.get(int(user_id))
    return render_template('backend/User/editUser.html', active_page='users', module=module, user=user)


@app.post('/admin/editUser')
def editUser():
    user_id = request.form["user_id"]
    username = request.form["username"]
    password = request.form["password"]

    user = db.session.get(User, int(user_id))
    if not user:
        return "User not found", 404

    user.username = username
    if password:  # Only update if password is provided
        user.password = generate_password_hash(password)
    db.session.commit()
    return redirect(url_for('users'))

@app.route('/admin/users/delete', methods=['POST'])
def deleteUser():
    user_id = request.args.get('user_id')
    user = db.session.get(User, int(user_id))
    if user:
        db.session.delete(user)
        db.session.commit()
    return redirect(url_for('users'))

