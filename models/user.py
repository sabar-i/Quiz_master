from models import db
from flask_login import UserMixin

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    full_name = db.Column(db.String(150), nullable=False)
    qualification = db.Column(db.String(150))
    dob = db.Column(db.Date)
    role = db.Column(db.String(10), nullable=False, default="user")  # "user" or "admin"


    def __repr__(self):
        return f"<User {self.email} - Role: {self.role}>"
