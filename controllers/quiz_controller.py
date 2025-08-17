from flask import Blueprint, render_template

quiz = Blueprint('quiz', __name__) 

@quiz.route('/start')
def start_quiz():
    return render_template('quiz.html')
