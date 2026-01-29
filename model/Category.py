from app import db
from sqlalchemy import text

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text )



def getAllCategory():
    sql = text("""
               SELECT *
               from category;
               """)
    results = db.session.execute(sql)
    rows = [dict(row._mapping) for row in results]
    return rows


def getCategoryById(category_id: int):
    sql = text("""
               SELECT *
               from category where category.id= :category_id;
               """)
    result = db.session.execute(sql, {'category_id': int(category_id)}).fetchone()
    if result:
        rows = dict(result._mapping)
        return rows
    else:
        return {"error": "Category not found"}
