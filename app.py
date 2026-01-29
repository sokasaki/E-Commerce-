from flask import Flask, render_template, request, redirect, url_for, jsonify, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime, timedelta
import os
import config
from upload_service import save_image
from config import SECRET_KEY

app = Flask(__name__)

app.config["SECRET_KEY"] = SECRET_KEY
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(hours=12)  # session TTL

app.config.from_object(config)
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///mydb.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Import models
from model import Product, Category, User


from routes.backend.auth import *
import routes


@app.before_request
def before_request():
    url = request.path
    if url.startswith('/admin') and not url.startswith('/login'):
        if not session.get("user_id"):
            flash("Please log in first.", "warning")
            return redirect(url_for("login", next=request.path))


@app.route('/admin/upload', methods=['GET', 'POST'])
def upload_image():
    images = None

    if request.method == 'POST':
        file = request.files.get('image')
        images = save_image(
            file,
            app.config['UPLOAD_FOLDER'],
            app.config['ALLOWED_EXTENSIONS']
        )

    return render_template('backend/add_product.html', images=images)


if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
