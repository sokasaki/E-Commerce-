from app import db
from sqlalchemy import text


# Define your models here
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    sku = db.Column(db.String(50), unique=True, nullable=False)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, nullable=False, default=0)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    description = db.Column(db.Text)
    image_url = db.Column(db.String(255))
    status = db.Column(db.String(20), default='active')  # active, inactive
    
    # Relationship to Category
    category = db.relationship('Category', backref='products', lazy=True)

    def to_dict(self):
        """Convert to format matching frontend templates"""
        from flask import url_for
        from model.Category import Category
        
        # Handle image URL
        image_url = self.image_url
        if image_url:
            if image_url.startswith(('http://', 'https://')):
                # External URL - use as is
                pass
            elif image_url.startswith('uploads/'):
                # Already has uploads/ prefix
                image_url = url_for('static', filename=image_url)
            elif image_url.startswith('static/'):
                # Has static/ prefix - remove it
                image_url = url_for('static', filename=image_url.replace('static/', '', 1))
            else:
                # Just a filename - add uploads/products/ prefix
                image_url = url_for('static', filename=f'uploads/products/{image_url}')
        
        # Get category using the relationship
        return {
            'id': self.id,
            'title': self.name,
            'price': self.price,
            'description': self.description,
            'category': self.category.name if self.category else 'Uncategorized',
            'image': image_url,
            'image_url': self.image_url,
            'stock': self.stock,
            'sku': self.sku,
            'status': self.status,
            'rating': {
                'rate': 4.5,
                'count': 100
            }
        }



def getAllProducts():
    sql = text("""
               SELECT product.*,
                      category.name as category_name
               from product
                        INNER JOIN category on product.category_id = category.id;
               """)
    results = db.session.execute(sql)
    rows = [dict(row._mapping) for row in results]
    return rows


def getAllProductsById(product_id: int):
    sql = text("""
               SELECT product.*,
                      category.name as category_name
               from product
                        INNER JOIN category on product.category_id = category.id
               where product.id = :product_id;
               """)
    result = db.session.execute(sql, {'product_id': int(product_id)}).fetchone()
    if result:
        rows = dict(result._mapping)
        return rows
    else:
        return {"error": "Product not found"}

