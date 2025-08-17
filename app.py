from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash  # Import for hashing passwords
from models import db  
from models.user import User  
from models.quiz import Quiz  
from controllers.main_controller import main  
from controllers.auth_controller import auth  
from controllers.quiz_controller import quiz  
from controllers.admin import admin_bp as admin  
from controllers.user_controller import user_bp

app = Flask(__name__)

# Configure SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quiz.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key'  # Required for Flask-WTF forms

db.init_app(app)  # Register SQLAlchemy with Flask app

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'  # Redirect to login if user is not authenticated

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# Register blueprints BEFORE app.run()
app.register_blueprint(main)
app.register_blueprint(auth, url_prefix='/auth')
app.register_blueprint(quiz, url_prefix='/quiz')  
app.register_blueprint(admin, url_prefix='/admin')  
app.register_blueprint(user_bp, url_prefix='/user')


# Ensure database tables exist and create an admin user
with app.app_context():
    db.create_all()

    # Check if admin exists, if not, create one
    admin_email = "admin@quiz.com"
    admin_user = User.query.filter_by(email=admin_email).first()

    if not admin_user:
        admin_user = User(
            full_name="Admin", 
            email=admin_email, 
            role="admin", 
            password=generate_password_hash("admin123")  # Hash the password for security
        )
        db.session.add(admin_user)
        db.session.commit()
        print("Admin user created: admin@quiz.com / admin123")

migrate = Migrate(app, db)

if __name__ == '__main__':
    app.run(debug=True)
