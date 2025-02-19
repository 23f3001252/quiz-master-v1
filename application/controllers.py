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
            return render_template("login")
        if this_user:
            if check_password_hash(this_user.password_hash, password):  
                session["username"] = username           
                if this_user.username == "admin":
                    flash("Logged in successfully.", "success") 
                    return redirect(url_for('admin_dash', username=username))
                flash("Logged in successfully.", "success")  
                return redirect(url_for('user_dash', username=username))   
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
        hashed_password = generate_password_hash(password)

        if user == "admin":
            return "One admin already exist. There is only one admin required."

        if user:
            #flash('Username already exists', 'warning')
            #return render_template('register.html')
            return "Username already exist."
        else:
            new_user = User(name=name, username=username, password_hash=hashed_password) # type: ignore
            db.session.add(new_user)
            db.session.commit()
            return render_template('login.html')
    return render_template('register.html')

#@app.route("/admin/<username>")
#def admin_dashboard(username):

#    return render_template("/admin/admin_dash.html", username=username)


# ==========================  ADMIN DASHBOARD  ==========================
@app.route("/admin/dashboard/<username>")
def admin_dash(username):
    if "username" not in session or session["username"] != username:
        flash("Unauthorized access!", "danger")
        return redirect(url_for("login"))

    subjects = Subject.query.all()
    chapters = Chapter.query.all()
    quizzes = Quiz.query.all()
    users = User.query.all()
    return render_template("admin/admin_dash.html", username=username, subjects=subjects, chapters=chapters, quizzes=quizzes, users=users)

# ==========================  SUBJECT MANAGEMENT  ==========================
@app.route("/admin/add_subject/<username>", methods=["GET", "POST"])
def add_subject(username):
    if request.method == "POST":
        name = request.form.get("subject_name")
        description = request.form.get("subject_desc")

        new_subject = Subject.query.filter_by(name=name).first()

        if new_subject:
            return "Subject already exist."
        new_subject = Subject(name=name, description=description) # type: ignore
        db.session.add(new_subject)
        db.session.commit()
        flash("Subject added successfully!", "success")
        return redirect(url_for("admin_dash", username=username))

    return render_template("admin/add_subject.html", username=username)

@app.route("/admin/edit_subject/<int:subject_id>", methods=["GET", "POST"])
def edit_subject(subject_id):
    subject = Subject.query.get_or_404(subject_id)

    if request.method == "POST":
        subject.name = request.form.get("subject_name")
        subject.description = request.form.get("subject_desc")

        db.session.commit()
        flash("Subject updated successfully!", "success")
        return redirect(url_for("admin_dash", username=session["username"], subject_id=subject.id))

    return render_template("admin/edit_subject.html", subject=subject, username=session["username"])

@app.route("/admin/delete_subject/<int:subject_id>")
def delete_subject(subject_id):
    subject = Subject.query.get_or_404(subject_id)

    # Manually delete all related chapters first
    Chapter.query.filter_by(subject_id=subject.id).delete()

    db.session.delete(subject)
    db.session.commit()
    flash("Subject deleted successfully!", "success")
    return redirect(url_for("admin_dash", username=session["username"], subject_id=subject.id))

# ==========================  CHAPTER MANAGEMENT  ==========================
@app.route("/admin/add_chapter/<username>", methods=["GET", "POST"])
def add_chapter(username):
    if request.method == "POST":
        chapter_name = request.form.get("chapter_name")
        subject_name = request.form.get("subject_name")
        description = request.form.get("chapter_desc")

        subject = Subject.query.filter_by(name=subject_name).first()
        chapter = Chapter.query.filter_by(name=chapter_name).first()
        if not subject:
            return "Subject not found! Please add the subject first."
        
        if chapter :
            return "Chapter already exist."
        new_chapter = Chapter(name=chapter_name, description=description, subject_id=subject.id) # type: ignore
        db.session.add(new_chapter)
        db.session.commit()
        flash("Chapter added successfully!", "success")

        return redirect(url_for("admin_dash", username=username))# chapter_id=chapter_id))

    return render_template("admin/add_chapter.html", username=username)

@app.route("/admin/edit_chapter/<int:chapter_id>", methods=["GET", "POST"])
def edit_chapter(chapter_id):
    chapter = Chapter.query.get_or_404(chapter_id)
    subject = Subject.query.get_or_404(chapter.subject_id)

    if request.method == "POST":
        chapter.name = request.form.get("chapter_name")
        chapter.subject_name = request.form.get("subject_name")
        chapter.description = request.form.get("chapter_desc")

        db.session.commit()
        flash("Chapter updated successfully!", "success")
        return redirect(url_for("admin_dash", username=session["username"], chapter_id=chapter.id))

    return render_template("admin/edit_chapter.html", chapter=chapter,subject=subject, username=session["username"])

@app.route("/admin/delete_chapter/<int:chapter_id>")
def delete_chapter(chapter_id):
    chapter = Chapter.query.get_or_404(chapter_id)
    db.session.delete(chapter)
    db.session.commit()
    flash("Chapter deleted successfully!", "success")
    return redirect(url_for("admin_dash", username=session["username"], chapter_id=chapter.id))

# ==========================  QUIZ MANAGEMENT  ==========================
@app.route("/admin/quiz_management")
def quiz_management():
    quizzes = Quiz.query.all()
    return render_template("admin/quiz_mng.html", username=session["username"], quizzes=quizzes)

@app.route("/admin/quiz_management/add_quiz", methods=["GET", "POST"])
def add_quiz():
    if request.method == "POST":
        title = request.form.get("title")
        chapter_id = request.form.get("chapter_id")
        duration = request.form.get("duration")
        quiz_date = datetime.strptime(request.form.get("date"), "%Y-%m-%d") # type: ignore

        new_quiz = Quiz(title=title, chapter_id=chapter_id, time_duration=duration, date_of_quiz=quiz_date) # type: ignore
        db.session.add(new_quiz)
        db.session.commit()
        flash("Quiz added successfully!", "success")

        return redirect(url_for("quiz_management", username=session["username"]))

    chapters = Chapter.query.all()
    return render_template("admin/add_quiz.html", username=session["username"], chapters=chapters)

@app.route("/admin/quiz_management/edit_quiz/<int:quiz_id>", methods=["GET", "POST"])
def edit_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)

    if request.method == "POST":
        quiz.title = request.form.get("title")
        quiz.chapter_id = request.form.get("chapter_id")
        quiz.duration = request.form.get("duration")
        quiz.quiz_date = datetime.strptime(request.form.get("date"), "%Y-%m-%d") # type: ignore

        db.session.commit()
        flash("Quiz updated successfully!", "success")
        return redirect(url_for("quiz_management", username=session["username"]))

    return render_template("admin/edit_quiz.html", username=session["username"])

@app.route("/admin/quiz_management/delete_quiz/<int:quiz_id>")
def delete_quiz(quiz_id):
    quiz = Chapter.query.get_or_404(quiz_id)
    db.session.delete(quiz)
    db.session.commit()
    flash("Chapters deleted successfully!", "success")
    return redirect(url_for("quiz_management", username=session["username"]))


@app.route("/admin/quiz_management/add_question", methods=["GET", "POST"])
def add_question():
    if request.method == "POST":
        quiz_id = request.form.get("quiz_id")
        question_text = request.form.get("question_statement")
        option1 = request.form.get("option1")
        option2 = request.form.get("option2")
        option3 = request.form.get("option3")
        option4 = request.form.get("option4")
        correct_option = request.form.get("correct_option")

        new_question = Question(
            quiz_id=quiz_id, # type: ignore
            question_statement=question_text, # type: ignore
            option1=option1, option2=option2, # type: ignore
            option3=option3, option4=option4, # type: ignore
            correct_option=int(correct_option) # type: ignore
        )
        db.session.add(new_question)
        db.session.commit()
        flash("Question added successfully!", "success")

        return redirect(url_for("quiz_management"))

    quizzes = Quiz.query.all()
    return render_template("admin/add_question.html", username=session["username"], quizzes=quizzes)

@app.route("/admin/quiz_management/edit_question/<int:question_id>", methods=["GET", "POST"])
def edit_question(question_id):
    ques = Quiz.query.get_or_404(question_id)

    if request.method == "POST":
        ques.quiz_id = request.form.get("quiz_id")
        ques.question_text = request.form.get("question_statement")
        ques.option1 = request.form.get("option1")
        ques.option2 = request.form.get("option2")
        ques.option3 = request.form.get("option3")
        ques.option4 = request.form.get("option4")
        ques.correct_option = request.form.get("correct_option")

        db.session.commit()
        flash("Question updated successfully!", "success")
        return redirect(url_for("quiz_management", username=session["username"]))

    return render_template("admin/edit_question.html", username=session["username"])

@app.route("/admin/quiz_management/delete_question/<int:question_id>")
def delete_question(question_id):
    ques = Chapter.query.get_or_404(question_id)
    db.session.delete(ques)
    db.session.commit()
    flash("Question deleted successfully!", "success")
    return redirect(url_for("quiz_management", username=session["username"]))

# ==========================  USER FUNCTIONALITY  ==========================
#@app.route("/user/dashboard/<username>")
#def user_dash(username):
#    subjects = Subject.query.all()
#    quizzes = Quiz.query.all()
#    return render_template("user/user_dash.html", username=username, subjects=subjects, quizzes=quizzes)

#@app.route("/user/quiz/<int:quiz_id>")
#def start_quiz(quiz_id):
#    quiz = Quiz.query.get_or_404(quiz_id)
#    questions = Question.query.filter_by(quiz_id=quiz_id).all()
#    return render_template("user/start_quiz.html", quiz=quiz, questions=questions, username=session["username"])

#@app.route("/user/quiz/submit/<int:quiz_id>", methods=["POST"])
#def submit_quiz(quiz_id):
#    quiz = Quiz.query.get_or_404(quiz_id)
#    questions = Question.query.filter_by(quiz_id=quiz_id).all()

#    total_score = 0
#    for question in questions:
#        user_answer = request.form.get(f"question_{question.id}")
#        if user_answer and int(user_answer) == question.correct_option:
#            total_score += 1

#    new_score = Score(
#        quiz_id=quiz_id,
#        user_id=session["user_id"],
#        total_scored=total_score
#    )
#    db.session.add(new_score)
#    db.session.commit()

#    flash(f"You scored {total_score}/{len(questions)}!", "success")
#    return redirect(url_for("user_dash", username=session["username"]))

#@app.route("/user/quiz_history/<username>")
#def quiz_history(username):
#    user = User.query.filter_by(username=username).first()
#    scores = Score.query.filter_by(user_id=user.id).all()
#    return render_template("user/quiz_score.html", username=username, scores=scores)

## ==========================  ADMIN SEARCH FUNCTIONALITY  ==========================
#@app.route("/admin/search", methods=["GET"])
#def admin_search():
#    query = request.args.get("query")
    
#    users = User.query.filter(User.username.ilike(f"%{query}%")).all()
#    subjects = Subject.query.filter(Subject.name.ilike(f"%{query}%")).all()
#    quizzes = Quiz.query.filter(Quiz.title.ilike(f"%{query}%")).all()

#    return render_template("admin/search_results.html", users=users, subjects=subjects, quizzes=quizzes, query=query)

## ==========================  LOGOUT  ==========================
#@app.route("/logout")
#def logout():
#    session.pop("username", None)
#    flash("Logged out successfully.", "success")
#    return redirect(url_for("login"))


## ==========================  USER MANAGEMENT  ==========================
#@app.route("/admin/users")
#def users_list():
#    users = User.query.all()
#    return render_template("admin/users.html", users=users, username=session["username"])

#@app.route("/admin/delete_user/<int:user_id>")
#def delete_user(user_id):
#    user = User.query.get_or_404(user_id)
#    db.session.delete(user)
#    db.session.commit()
#    flash("User deleted successfully!", "success")
#    return redirect(url_for("users_list"))




#@app.route("/dashboard/<username>")
#def admin_dash(username):

#    return render_template("/admin/admin_dash.html", username=username)

#@app.route("/<string:username>/add_chapter", methods = ["GET", "POST"])
#def add_chapter(username):
#    if request.method == "POST":
#        name = request.form.get("chapter_name")
#        sub_name = request.form.get("subject_name")
#        description = request.form.get("chapter_desc")

#        new_chap = Chapter.query.filter_by(name=name).first()

#        if new_chap :
#            return "Chapter already exist."
#        new_chap = Chapter(name=name, description=description, subject_id=Subject.id)
#        db.session.add(new_chap)
#        db.session.commit()
#        return render_template("/admin/admin_dash.html", username=username)
#    return render_template("/admin/add_chapter.html", username=username)


#@app.route("/admin/add_subject")
#def add_subject():
#    return render_template("/admin/add_subject.html")

#@app.route("/admin/quiz_management")
#def quiz_management():
#    return render_template("/admin/quiz_mng.html")

#@app.route("/admin/quiz_management/add_question")
#def add_question():
#    return render_template("/admin/add_question.html")

#@app.route("/admin/quiz_management/add_quiz")
#def add_quiz():
#    return render_template("/admin/add_quiz.html")

#@app.route("/admin/quiz_management/summary")
#def admin_quiz_summary():
#    return render_template("/admin/admin_summary.html")

##### User activities.
#@app.route("/user/<username>")
#def user_dash(username):
#    return render_template("/user/user_dash.html", username=username)

#@app.route("/user/quiz_score")
#def quiz_score():
#    return render_template("/user/quiz_score.html")

#@app.route("/user/quiz_question")
#def start_quiz():
#    return render_template("/user/start_quiz.html")

#@app.route("/user/view_quiz")
#def view_quiz():
#    return render_template("/user/view_quiz.html")

#@app.route("/user/quiz_summary")
#def user_quiz_summary():
#    return render_template("/user/user_summary.html")
