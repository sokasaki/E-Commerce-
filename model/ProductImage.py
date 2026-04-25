from app import db

class ProductImage(db.Model):
    __tablename__ = 'product_image'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id', ondelete='CASCADE'), nullable=False)
    image_url = db.Column(db.String(255), nullable=False)
    is_primary = db.Column(db.Boolean, default=False)  # Mark the main image
    display_order = db.Column(db.Integer, default=0)  # Order for display
    
    # Relationship back to Product
    product = db.relationship('Product', back_populates='images')
    
    def __repr__(self):
        return f'<ProductImage {self.id}: {self.image_url} (Product: {self.product_id})>'
    
    def get_full_url(self):
        """Get the full URL for the image"""
        from flask import url_for
        if self.image_url:
            if self.image_url.startswith(('http://', 'https://')):
                return self.image_url
            elif self.image_url.startswith('uploads/'):
                return url_for('static', filename=self.image_url)
            else:
                return url_for('static', filename=f'uploads/products/{self.image_url}')
        return None
