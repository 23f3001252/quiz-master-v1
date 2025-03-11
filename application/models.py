from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from flask_bcrypt import Bcrypt
from datetime import datetime

bcrypt = Bcrypt()

import random

def generate_custom_id(model, prefix):
    while True:
        unique_id = f"{prefix}{random.randint(100, 999)}"
        if not model.query.filter_by(id=unique_id).first():
            return unique_id

class User(db.Model):
    id = db.Column(db.String(10), primary_key=True, default=lambda: generate_custom_id(User, "US"))
    name = db.Column(db.String(50), nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    type = db.Column(db.String(120), default="user", nullable=False)

    scores = db.relationship('Score', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)


class Subject(db.Model):
    id = db.Column(db.String(10), primary_key=True, default=lambda: generate_custom_id(Subject, "SB"))
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)

    chapters = db.relationship('Chapter', backref='subject', lazy=True, cascade='all, delete')


class Chapter(db.Model):
    id = db.Column(db.String(10), primary_key=True, default=lambda: generate_custom_id(Chapter, "CH"))
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id', ondelete="CASCADE"), nullable=False) #when a subject is deleted, its chapters are also deleted automatically.

    quizzes = db.relationship('Quiz', backref='chapter', cascade="all, delete", lazy=True)


class Quiz(db.Model):
    id = db.Column(db.String(10), primary_key=True, default=lambda: generate_custom_id(Quiz, "QZ"))
    title = db.Column(db.String(120), nullable=False)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapter.id', ondelete='CASCADE'), nullable=False)
    date_of_quiz = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    time_duration = db.Column(db.String(10), nullable=False)  # HH:MM format
    remarks = db.Column(db.Text, nullable=True)

    questions = db.relationship('Question', backref='quiz', lazy=True, cascade='all, delete')
    scores = db.relationship('Score', backref='quiz', lazy=True, cascade='all, delete')


class Question(db.Model):
    id = db.Column(db.String(10), primary_key=True, default=lambda: generate_custom_id(Question, "QS"))
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id', ondelete="CASECADE"), nullable=False)
    question_statement = db.Column(db.Text, nullable=False)
    option1 = db.Column(db.String(200), nullable=False)
    option2 = db.Column(db.String(200), nullable=False)
    option3 = db.Column(db.String(200), nullable=True)
    option4 = db.Column(db.String(200), nullable=True)
    correct_option = db.Column(db.Integer, nullable=False)  # 1,2,3,4 to indicate correct answer


class Score(db.Model):
    id = db.Column(db.String(10), primary_key=True, default=lambda: generate_custom_id(Score, "SC"))
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    time_stamp_of_attempt = db.Column(db.DateTime, default=datetime.utcnow)
    total_scored = db.Column(db.Integer, nullable=False)


