from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()
from models.user_score import UserScore

from .user import User
from .quiz import Subject
from .quiz import Chapter
from .quiz import Quiz
from .quiz import Question