import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

SECRET_KEY = "adscasedwq"

UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static/uploads/products')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
MAX_CONTENT_LENGTH = 2 * 1024 * 1024  # 2MB
