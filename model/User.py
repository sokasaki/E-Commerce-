from app import db
from sqlalchemy import text
from datetime import datetime

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


def getAllUsers():
    # ORM query, returns list of User objects
    return User.query.all()

def getUserById(user_id: int):
    sql = text("""
               SELECT *
               from user
               where user.id = :user_id;
               """)
    result = db.session.execute(sql, {'user_id': int(user_id)}).fetchone()
    if result:
        rows = dict(result._mapping)
        return rows
    else:
        return {"error": "User not found"}