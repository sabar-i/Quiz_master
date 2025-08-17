from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import db, User, Subject, Chapter, Quiz, UserScore, Question
from datetime import datetime
from flask import jsonify

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Admin Dashboard
@admin_bp.route('/')
def dashboard():
    users = User.query.all()
    subjects = Subject.query.all()
    chapters = Chapter.query.all()
    quizzes = Quiz.query.all()
    quiz_scores = UserScore.query.all()
    quiz_stats = []

    for quiz in quizzes:
       scores = UserScore.query.filter_by(quiz_id=quiz.id).all()
    
       highest = max((score.score for score in scores), default=0)
       lowest = min((score.score for score in scores), default=0)
       avg = sum(score.score for score in scores) / len(scores) if scores else 0

       quiz_stats.append({
          "title": quiz.title or "Unknown",
          "highest": highest,
          "lowest": lowest,
          "average": avg
       })


    return render_template('admin_dashboard.html', users=users, subjects=subjects, 
                           chapters=chapters, quizzes=quizzes, quiz_scores=quiz_scores, quiz_stats=quiz_stats)
# CRUD for Users
@admin_bp.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    if request.method == 'POST':
        user.full_name = request.form['full_name']
        user.email = request.form['email']
        user.role = request.form['role']
        db.session.commit()
        flash('User updated successfully!', 'success')
        return redirect(url_for('admin.dashboard'))
    return render_template('edit_user.html', user=user)

@admin_bp.route('/delete_user/<int:user_id>')
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash('User deleted successfully!', 'danger')
    return redirect(url_for('admin.dashboard'))

# CRUD for Subjects
@admin_bp.route('/create_subject', methods=['POST'])
def create_subject():
    name = request.form['name']
    description = request.form['description']
    new_subject = Subject(name=name, description=description)
    db.session.add(new_subject)
    db.session.commit()
    flash('Subject added successfully!', 'success')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/edit_subject/<int:subject_id>', methods=['GET', 'POST'])
def edit_subject(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    if request.method == 'POST':
        subject.name = request.form['name']
        subject.description = request.form['description']
        db.session.commit()
        flash('Subject updated successfully!', 'success')
        return redirect(url_for('admin.dashboard'))
    return render_template('edit_subject.html', subject=subject)

@admin_bp.route('/delete_subject/<int:subject_id>')
def delete_subject(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    db.session.delete(subject)
    db.session.commit()
    flash('Subject deleted successfully!', 'danger')
    return redirect(url_for('admin.dashboard'))

# CRUD for Chapters
@admin_bp.route('/create_chapter', methods=['POST'])
def create_chapter():
    name = request.form['name']
    description = request.form['description']
    subject_id = request.form['subject_id']
    new_chapter = Chapter(name=name, description=description, subject_id=subject_id)
    db.session.add(new_chapter)
    db.session.commit()
    flash('Chapter added successfully!', 'success')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/edit_chapter/<int:chapter_id>', methods=['GET', 'POST'])
def edit_chapter(chapter_id):
    chapter = Chapter.query.get_or_404(chapter_id)
    subjects = Subject.query.all()
    if request.method == 'POST':
        chapter.name = request.form['name']
        chapter.description = request.form['description']
        chapter.subject_id = request.form['subject_id']
        db.session.commit()
        flash('Chapter updated successfully!', 'success')
        return redirect(url_for('admin.dashboard'))
    return render_template('edit_chapter.html', chapter=chapter, subjects=subjects)

@admin_bp.route('/delete_chapter/<int:chapter_id>')
def delete_chapter(chapter_id):
    chapter = Chapter.query.get_or_404(chapter_id)
    db.session.delete(chapter)
    db.session.commit()
    flash('Chapter deleted successfully!', 'danger')
    return redirect(url_for('admin.dashboard'))

# CRUD for Quizzes
@admin_bp.route('/create_quiz', methods=['POST'])
def create_quiz():
    title = request.form['title']
    chapter_id = request.form['chapter_id']
    date_of_quiz=datetime.strptime(request.form['date_of_quiz'], "%Y-%m-%d").date()
    time_duration=datetime.strptime(request.form['time_duration'], "%H:%M").time()
    remarks = request.form.get('remarks', None)
    new_quiz = Quiz(title=title, chapter_id=chapter_id, date_of_quiz=date_of_quiz, time_duration=time_duration, remarks=remarks)
    db.session.add(new_quiz)
    db.session.commit()
    flash('Quiz added successfully!', 'success')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/edit_quiz/<int:quiz_id>', methods=['GET', 'POST'])
def edit_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    chapters = Chapter.query.all()
    if request.method == 'POST':
        quiz.title = request.form['title']
        quiz.chapter_id = request.form['chapter_id']
        
        # Convert date_of_quiz to a Python date object
        date_of_quiz_str = request.form.get('date_of_quiz')
        if date_of_quiz_str:
            quiz.date_of_quiz = datetime.strptime(date_of_quiz_str, "%Y-%m-%d").date()

        # Convert time_duration to an integer
        time_duration_str = request.form.get('time_duration')
        if time_duration_str:
            time_duration_str = time_duration_str[:5]  # Keeps only "HH:MM"
            quiz.time_duration = datetime.strptime(time_duration_str, "%H:%M").time()

        quiz.remarks = request.form.get('remarks', None)  # Can be None if not provided
        db.session.commit()

        flash('Quiz updated successfully!', 'success')
        return redirect(url_for('admin.dashboard'))
    return render_template('edit_quiz.html', quiz=quiz, chapters=chapters)

@admin_bp.route('/delete_quiz/<int:quiz_id>')
def delete_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)

    # Delete related records first
    Question.query.filter_by(quiz_id=quiz.id).delete()
    db.session.commit()  # Commit before deleting the quiz

    db.session.delete(quiz)
    db.session.commit()

    flash('Quiz deleted successfully!', 'danger')
    return redirect(url_for('admin.dashboard'))


# View Quiz Scores
@admin_bp.route('/quiz_scores')
def quiz_scores():
    scores = UserScore.query.all()
    for score in scores:
        print(f"User ID: {score.user_id}, Quiz ID: {score.quiz_id}, Score: {score.score}, Date: {score.date_taken}")
    return render_template('admin_dashboard.html', quiz_scores=scores)

# Edit Quiz Score
@admin_bp.route('/edit_quiz_score/<int:score_id>', methods=['GET', 'POST'])
def edit_quiz_score(score_id):
    score = UserScore.query.get_or_404(score_id)
    
    if request.method == 'POST':
        new_score = request.form.get('score')
        
        if new_score.isdigit():
            score.score = int(new_score)
            db.session.commit()
            flash('Quiz score updated successfully!', 'success')
            return redirect(url_for('admin.dashboard'))
        else:
            flash('Invalid score!', 'danger')

    return render_template('edit_quiz_score.html', score=score)

# Delete Quiz Score
@admin_bp.route('/delete_quiz_score/<int:score_id>', methods=['POST'])
def delete_quiz_score(score_id):
    score = UserScore.query.get_or_404(score_id)
    db.session.delete(score)
    db.session.commit()
    flash('Quiz score deleted!', 'success')
    return redirect(url_for('admin.dashboard'))

# Route to Add Questions
@admin_bp.route('/add_questions/<int:quiz_id>', methods=['GET', 'POST'])
def add_questions(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)

    if request.method == 'POST':
        question_text = request.form['question_text']
        option_1 = request.form['option_1']
        option_2 = request.form['option_2']
        option_3 = request.form['option_3']
        option_4 = request.form['option_4']
        correct_answer = request.form['correct_answer']

        new_question = Question(
            quiz_id=quiz.id,
            question_text=question_text,
            option_1=option_1,
            option_2=option_2,
            option_3=option_3,
            option_4=option_4,
            correct_answer=correct_answer
        )

        db.session.add(new_question)
        db.session.commit()
        flash('Question added successfully!', 'success')
        return redirect(url_for('admin.add_questions', quiz_id=quiz.id))

    return render_template('add_questions.html', quiz_id=quiz.id)


# Route to Edit Questions
@admin_bp.route('/edit_questions/<int:quiz_id>', methods=['GET', 'POST'])
def edit_questions(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = Question.query.filter_by(quiz_id=quiz_id).all()

    if request.method == 'POST':
        for question in questions:
            question_text = request.form.get(f'question_text_{question.id}')
            option_1 = request.form.get(f'option_1_{question.id}')
            option_2 = request.form.get(f'option_2_{question.id}')
            option_3 = request.form.get(f'option_3_{question.id}')
            option_4 = request.form.get(f'option_4_{question.id}')
            correct_answer = request.form.get(f'correct_answer_{question.id}')

            question.question_text = question_text
            question.option_1 = option_1
            question.option_2 = option_2
            question.option_3 = option_3
            question.option_4 = option_4
            question.correct_answer = correct_answer

        db.session.commit()
        flash('Questions updated successfully!', 'success')
        return redirect(url_for('admin.edit_questions', quiz_id=quiz.id))

    return render_template('edit_questions.html', quiz=quiz, questions=questions)

@admin_bp.route("/search", methods=["GET"])
def search():
    query = request.args.get("query", "").strip()
    category = request.args.get("category", "").strip()

    if not query:
        return render_template("admin_dashboard.html", error="Please enter a search query.")

    results = []
    
    if category == "users":
        results = User.query.filter(User.full_name.ilike(f"%{query}%") | User.email.ilike(f"%{query}%")).all()
    elif category == "subjects":
        results = Subject.query.filter(Subject.name.ilike(f"%{query}%")).all()
    elif category == "quizzes":
        results = Quiz.query.filter(Quiz.title.ilike(f"%{query}%")).all()
    elif category == "questions":
        results = Question.query.filter(Question.text.ilike(f"%{query}%")).all()
    
    return render_template("admin_search_results.html", results=results, category=category, query=query)
@admin_bp.route('/get_chapters/<int:subject_id>', methods=['GET'])
def get_chapters(subject_id):
    print(f"📌 DEBUG: Received request for subject_id: {subject_id}")  # Debug log

    chapters = Chapter.query.filter_by(subject_id=subject_id).all()

    if not chapters:
        print(f"⚠️ No chapters found for subject_id: {subject_id}")  # Debug log

    return jsonify([{'id': chapter.id, 'name': chapter.name} for chapter in chapters])








