from models import db

class UserScore(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)  # Added Quiz reference
    score = db.Column(db.Integer, nullable=False)
    date_taken = db.Column(db.DateTime, default=db.func.current_timestamp())

    user = db.relationship('User', backref='scores')
    quiz = db.relationship('Quiz', backref='scores')  # Establish relationship with Quiz
