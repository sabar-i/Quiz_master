from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import Quiz, Question, UserScore, db
from datetime import datetime
from flask import Blueprint
from flask import jsonify
from sqlalchemy.sql import func

user_bp = Blueprint('user', __name__)

# User Dashboard: Show available quizzes and past scores
@user_bp.route('/user_dashboard')
@login_required
def user_dashboard():
    quizzes = Quiz.query.all()
    scores = UserScore.query.filter_by(user_id=current_user.id).all()

    # Fetch performance data for each quiz
    performance_data = []
    for quiz in quizzes:
        highest_user_score = (
            db.session.query(func.max(UserScore.score))
            .filter(UserScore.user_id == current_user.id, UserScore.quiz_id == quiz.id)
            .scalar()
        ) or 0

        highest_score = (
            db.session.query(func.max(UserScore.score))
            .filter(UserScore.quiz_id == quiz.id)
            .scalar()
        ) or 0

        average_score = (
            db.session.query(func.avg(UserScore.score))
            .filter(UserScore.quiz_id == quiz.id)
            .scalar()
        ) or 0

        performance_data.append({
            "quiz_title": quiz.title,
            "user_highest": highest_user_score,
            "highest_score": highest_score,
            "average_score": round(average_score, 2)
        })

    return render_template("user_dashboard.html", quizzes=quizzes, scores=scores, performance_data=performance_data)


# Start Quiz: Display questions with Timer
@user_bp.route('/start_quiz/<int:quiz_id>', methods=['GET', 'POST'])
@login_required
def start_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = Question.query.filter_by(quiz_id=quiz_id).all()

    # Convert `hh:mm` (time_duration) to total seconds
    time_parts = str(quiz.time_duration).split(':')  # Convert `hh:mm` to list [hh, mm]
    total_seconds = int(time_parts[0]) * 3600 + int(time_parts[1]) * 60  # Convert to seconds

    if request.method == 'POST':
        score = 0
        for question in questions:
            user_answer = request.form.get(f'question_{question.id}')
            correct_answer = getattr(question, question.correct_answer)  # Get the actual answer text

            print(f"User Answer: {user_answer}, Correct Answer: {correct_answer}")  # Debugging

            if user_answer and user_answer.strip().lower() == correct_answer.strip().lower():
                score += 1

        # Save score in database
        new_score = UserScore(user_id=current_user.id, quiz_id=quiz_id, score=score, date_taken=datetime.utcnow())
        db.session.add(new_score)
        db.session.commit()

        flash(f'Quiz Completed! Your Score: {score}/{len(questions)}', 'success')
        return redirect(url_for('user.user_dashboard'))

    return render_template('start_quiz.html', quiz=quiz, questions=questions, total_seconds=total_seconds)



@user_bp.route('/scores')
@login_required
def user_scores():
    scores = UserScore.query.filter_by(user_id=current_user.id).all()
    return render_template('user_scores.html', scores=scores)



