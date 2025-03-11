from flask import jsonify, request
from flask_restful import Api, Resource
#from application.controllers import app
from flask import current_app as app
from application.models import *

api = Api(app)

# Subject Resource
class SubjectResource(Resource):
    def get(self):
        subjects = Subject.query.all()
        return jsonify([{"id": subject.id, "name": subject.name, "description": subject.description} for subject in subjects])

# Chapter Resource
class ChapterResource(Resource):
    def get(self):
        chapters = Chapter.query.all()
        return jsonify([{
            "id": chapter.id,
            "name": chapter.name,
            "subject_id": chapter.subject_id,
            "description": chapter.description
        } for chapter in chapters])

# Quiz Resource
class QuizResource(Resource):
    #def get(self):
    #    quizzes = Quiz.query.all()

    def get(self):
        chapter_id = request.args.get('chapter_id')
        if chapter_id:
            quizzes = Quiz.query.filter_by(chapter_id=chapter_id).all()
        else:
            quizzes = Quiz.query.all()

        return jsonify([{
            "id": quiz.id,
            "title": quiz.title,
            "chapter_id": quiz.chapter_id,
            "date_of_quiz": quiz.date_of_quiz.strftime("%Y-%m-%d"),
            "time_duration": quiz.time_duration,
            "remarks": quiz.remarks
        } for quiz in quizzes])

# Score Resource
class ScoreResource(Resource):
    def get(self):
        scores = Score.query.all()
        return jsonify([{
            "id": score.id,
            "user_id": score.user_id,
            "quiz_id": score.quiz_id,
            "total_scored": score.total_scored,
            "time_stamp_of_attempt": score.time_stamp_of_attempt.strftime("%Y-%m-%d %H:%M:%S")
        } for score in scores])

# Add resources to API
api.add_resource(SubjectResource, '/api/subjects')
api.add_resource(ChapterResource, '/api/chapters')
api.add_resource(QuizResource, '/api/quizzes')
api.add_resource(ScoreResource, '/api/scores')
