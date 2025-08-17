from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required,current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models.user import User 
from models.quiz import Quiz  
from models import db 


from forms import RegistrationForm, LoginForm

auth = Blueprint('auth', __name__)

# Signup route
@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='pbkdf2:sha256')
        new_user = User(
            email=form.email.data,
            password=hashed_password,
            full_name=form.full_name.data,  
            qualification=form.qualification.data,  
            dob=form.dob.data  
        )
        try:
            db.session.add(new_user)
            db.session.commit()
            flash('Account created successfully!', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            print("Error:", e)  # Debugging line
            flash("Database error! Check logs.", "danger")
    
    return render_template('signup.html', form=form)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()  

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        print(f"Email Entered: {email}")  # Debugging
        print(f"Password Entered: {password}")  # Debugging

        user = User.query.filter_by(email=email).first()

        if not user:
            flash("User does not exist. Please sign up.", "danger")
            return redirect(url_for('auth.login'))

        if not check_password_hash(user.password, password):
            flash("Incorrect password. Please try again.", "danger")
            return redirect(url_for('auth.login'))

        print("User found, trying to log in...")  # Debugging
        login_user(user)  

        print("User logged in!")  # Debugging

        flash("Login successful!", "success")
        return redirect(url_for('user.user_dashboard'))  

    return render_template('login.html', form=form)

@auth.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if not user:
            flash("User does not exist.", "danger")
            return redirect(url_for('auth.admin_login'))

        if not check_password_hash(user.password, form.password.data):
            flash("Incorrect password.", "danger")
            return redirect(url_for('auth.admin_login'))

        if user.role != "admin":
            flash("Access denied! You are not an admin.", "danger")
            return redirect(url_for('auth.admin_login'))

        login_user(user)
        flash("Admin login successful!", "success")
        return redirect(url_for('admin.dashboard'))  # Redirect to admin dashboard

    return render_template('admin_login.html', form=form)
@auth.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if current_user.role != "admin":
        flash("Access denied! You are not an admin.", "danger")
        return redirect(url_for('main.dashboard'))  # Redirect non-admin users

    return render_template('admin_dashboard.html')

# Logout route
@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))
