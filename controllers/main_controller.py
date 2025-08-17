from flask import Blueprint, render_template
from flask_login import login_required, current_user
from models.user_score import UserScore

main = Blueprint('main', __name__)

@main.route('/')
def home():
    return render_template('home.html')

@main.route('/dashboard')
@login_required
def dashboard():
    scores = UserScore.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', scores=scores)
