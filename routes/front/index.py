from app import app, render_template
from model.Product import Product
import logging

logger = logging.getLogger(__name__)


@app.get('/')
@app.route('/home')
def home():
    products = Product.query.limit(4).all()
    products = [p.to_dict() for p in products]
    return render_template("front/index.html", products=products)