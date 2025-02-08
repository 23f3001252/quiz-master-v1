from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
#from models import db, User 


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quiz_master.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

#db.init_app(app)
with app.app_context():
    db.create_all()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/admin")
def admin_dash():
    return render_template("/admin/admin_dash.html")

@app.route("/admin/add_chapter")
def add_chapter():  
    return render_template("/admin/add_chapter.html")

@app.route("/admin/add_subject")
def add_subject():
    return render_template("/admin/add_subject.html")

@app.route("/admin/quiz_management")
def quiz_management():
    return render_template("/admin/quiz_mng.html")

@app.route("/admin/quiz_management/add_question")
def add_question():
    return render_template("/admin/add_question.html")

@app.route("/admin/quiz_management/add_quiz")
def add_quiz():
    return render_template("/admin/add_quiz.html")


if __name__ == "__main__":
    app.run(debug=True)

