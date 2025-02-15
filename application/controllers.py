from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask import current_app as app
from .models import *


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        this_user = User.query.filter_by(username=username).first()
        
        if not username or not password:
            flash('Please fill out all fields', 'warning')
            return redirect(url_for('login'))
        if this_user:
            if this_user.password_hash == password:             
                if this_user.username == "admin":
                    flash("Logged in successfully.", "success") 
                    return redirect(url_for('admin_dash'))
                flash("Logged in successfully.", "success")  
                return redirect(url_for('user_dash'))   
            #flash("Incorrect password", "danger")
            #return render_template('login.html')
            return "Incorrect password."
        #flash("User does not exist", "warning")
        #return render_template('login.html')
        return "User does not exist."
    return render_template('login.html')

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get('name')
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if not username or not password or not confirm_password:
            #flash('Please fill out all fields', "warning")
            #return render_template('register.html')
            return "Please fill out all fields."
        
        if password != confirm_password:
            #flash('Passwords do not match', 'warning')
            #return render_template('register.html')
            return "Password do not match."
        
        user = User.query.filter_by(username=username).first()

        if user:
            #flash('Username already exists', 'warning')
            #return render_template('register.html')
            return "Username already exist."
        else:
            new_user = User(name=name, username=username, password_hash=password) # type: ignore
            db.session.add(new_user)
            db.session.commit()
            return render_template('login.html')
    return render_template('register.html')


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

@app.route("/admin/quiz_management/summary")
def admin_quiz_summary():
    return render_template("/admin/admin_summary.html")

#### User activities.
@app.route("/user")
def user_dash():
    return render_template("/user/user_dash.html")

@app.route("/user/quiz_score")
def quiz_score():
    return render_template("/user/quiz_score.html")

@app.route("/user/quiz_question")
def start_quiz():
    return render_template("/user/start_quiz.html")

@app.route("/user/view_quiz")
def view_quiz():
    return render_template("/user/view_quiz.html")

@app.route("/user/quiz_summary")
def user_quiz_summary():
    return render_template("/user/user_summary.html")
