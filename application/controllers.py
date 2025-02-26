from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask import current_app as app
from .models import *


@app.route("/")
def index():
    return render_template("index.html")

# ==========================  LOGIN & REGISTRATION  ==========================

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        this_user = User.query.filter_by(username=username).first()

        if not username or not password:
            return "Please fill out all fields"
        
        if this_user :
            if check_password_hash(this_user.password_hash, password):
                session["user_id"] = this_user.id
                session["username"] = username
                flash("Logged in successfully.", "success")
                if this_user.username == "admin":
                    return redirect(url_for('admin_dash', username=username))
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

        if not name or not username or not password or not confirm_password:
            return "Please fill out all fields."
        
        if password != confirm_password:
            return "Passwords do not match"
        
        user = User.query.filter_by(username=username).first()
        if user:
            flash('Username already exists.', 'warning')
            return render_template('register.html')
        
        hashed_password = generate_password_hash(password)
        new_user = User(id=generate_custom_id(User, "US"), name=name, username=username, password_hash=hashed_password) # type: ignore
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    
    return render_template('register.html')


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
        
        if Subject.query.filter_by(name=name).first():
            flash("Subject already exists.", "warning")
            return render_template("admin/add_subject.html", username=username)

        new_subject = Subject(id=generate_custom_id(Subject, "SB"), name=name, description=description) # type: ignore
        db.session.add(new_subject)
        db.session.commit()
        return redirect(url_for("admin_dash", username=username))
    
    return render_template("admin/add_subject.html", username=username)

@app.route("/admin/edit_subject/<subject_id>", methods=["GET", "POST"])
def edit_subject(subject_id):
    subject = Subject.query.get_or_404(subject_id)

    if request.method == "POST":
        subject.name = request.form.get("subject_name")
        subject.description = request.form.get("subject_desc")

        db.session.commit()
        return redirect(url_for("admin_dash", username=session["username"]))

    return render_template("admin/edit_subject.html", subject=subject, username=session["username"])

@app.route("/admin/delete_subject/<subject_id>")
def delete_subject(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    Chapter.query.filter_by(subject_id=subject.id).delete()
    db.session.delete(subject)
    db.session.commit()
    return redirect(url_for("admin_dash", username=session["username"]))


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
        
        new_chapter = Chapter(id=generate_custom_id(Chapter, "CH"), name=chapter_name, description=description, subject_id=subject.id) # type: ignore
        db.session.add(new_chapter)
        db.session.commit()
        return redirect(url_for("admin_dash", username=username))
    
    return render_template("admin/add_chapter.html", username=username)

@app.route("/admin/edit_chapter/<chapter_id>", methods=["GET", "POST"])
def edit_chapter(chapter_id):
    chapter = Chapter.query.get_or_404(chapter_id)
    subject = Subject.query.get_or_404(chapter.subject_id)

    if request.method == "POST":
        chapter.name = request.form.get("chapter_name")
        chapter.description = request.form.get("chapter_desc")

        db.session.commit()
        return redirect(url_for("admin_dash", username=session["username"]))

    return render_template("admin/edit_chapter.html", chapter=chapter, subject=subject, username=session["username"])

@app.route("/admin/delete_chapter/<chapter_id>")
def delete_chapter(chapter_id):
    chapter = Chapter.query.get_or_404(chapter_id)
    db.session.delete(chapter)
    db.session.commit()
    return redirect(url_for("admin_dash", username=session["username"]))

# ==========================  QUIZ MANAGEMENT  ==========================

@app.route("/admin/quiz_management")
def quiz_management():
    if "username" not in session:
        return "Please log in first."

    quizzes = Quiz.query.all()
    return render_template("admin/quiz_mng.html", username=session["username"], quizzes=quizzes)

@app.route("/admin/quiz_management/add_quiz", methods=["GET", "POST"])
def add_quiz():
    if request.method == "POST":
        title = request.form.get("title")
        chapter_id = request.form.get("chapter_id")
        duration = request.form.get("duration")
        quiz_date = datetime.strptime(request.form.get("date"), "%Y-%m-%d") # type: ignore

        new_quiz = Quiz(id=generate_custom_id(Quiz, "QZ"), title=title, chapter_id=chapter_id, time_duration=duration, date_of_quiz=quiz_date) # type: ignore
        db.session.add(new_quiz)
        db.session.commit()
        flash("Quiz added successfully!", "success")

        return redirect(url_for("quiz_management", username=session["username"]))

    chapters = Chapter.query.all()
    return render_template("admin/add_quiz.html", username=session["username"], chapters=chapters)

@app.route("/admin/quiz_management/edit_quiz/<quiz_id>", methods=["GET", "POST"])
def edit_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)

    if request.method == "POST":
        quiz.title = request.form.get("title")
        quiz.chapter_id = request.form.get("chapter_id")
        quiz.time_duration = request.form.get("duration")
        quiz.date_of_quiz = datetime.strptime(request.form.get("date"), "%Y-%m-%d") # type: ignore

        db.session.commit()
        flash("Quiz updated successfully!", "success")
        return redirect(url_for("quiz_management", username=session["username"]))

    return render_template("admin/edit_quiz.html", username=session["username"], quiz=quiz)

@app.route("/admin/quiz_management/delete_quiz/<quiz_id>")
def delete_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)

    Question.query.filter_by(quiz_id=quiz.id).delete()
    db.session.delete(quiz)
    db.session.commit()
    flash("Quiz deleted successfully!", "success")
    return redirect(url_for("quiz_management", username=session["username"]))

@app.route("/admin/quiz_management/add_question", methods=["GET", "POST"])
def add_question():
    if request.method == "POST":
        quiz_id = request.form.get("quiz_id")
        quiz = Quiz.query.get(quiz_id)
        if not quiz:
            flash("Invalid quiz selected!", "danger")
            return redirect(url_for("add_question"))

        new_question = Question(
            id=generate_custom_id(Question, "QS"), # type: ignore
            quiz_id=quiz_id, # type: ignore
            question_statement=request.form.get("question_statement"), # type: ignore
            option1=request.form.get("option1"), # type: ignore
            option2=request.form.get("option2"), # type: ignore
            option3=request.form.get("option3"), # type: ignore
            option4=request.form.get("option4"), # type: ignore
            correct_option=int(request.form.get("correct_option")), # type: ignore
        )
        db.session.add(new_question)
        db.session.commit()
        flash("Question added successfully!", "success")
        return redirect(url_for("quiz_management", username=session["username"]))

    quizzes = Quiz.query.all()
    return render_template("admin/add_question.html", username=session["username"], quizzes=quizzes)


@app.route("/admin/quiz_management/edit_question/<question_id>", methods=["GET", "POST"])
def edit_question(question_id):
    question = Question.query.get_or_404(question_id)

    if request.method == "POST":
        question.quiz_id = request.form.get("quiz_id")
        question.question_statement = request.form.get("question_statement")
        question.option1 = request.form.get("option1")
        question.option2 = request.form.get("option2")
        question.option3 = request.form.get("option3")
        question.option4 = request.form.get("option4")
        question.correct_option = int(request.form.get("correct_option")) # type: ignore

        db.session.commit()
        flash("Question updated successfully!", "success")
        return redirect(url_for("quiz_management", username=session["username"]))

    return render_template("admin/edit_question.html", username=session["username"], question=question)

@app.route("/admin/quiz_management/delete_question/<question_id>")
def delete_question(question_id):
    question = Question.query.get_or_404(question_id)
    db.session.delete(question)
    db.session.commit()
    flash("Question deleted successfully!", "success")
    return redirect(url_for("quiz_management"))


# ==========================  USER DASHBOARD AND QUIZ ATTEMPT  ==========================

@app.route("/user/dashboard/<username>")
def user_dash(username):
    if "username" not in session or session["username"] != username:
        flash("Unauthorized access!", "danger")
        return redirect(url_for("login"))

    subjects = Subject.query.all()
    quizzes = Quiz.query.all()
    return render_template("user/user_dash.html", username=username, subjects=subjects, quizzes=quizzes)


@app.route("/user/attempt_quiz/<quiz_id>", methods=["GET", "POST"])
def attempt_quiz(quiz_id):
    if "username" not in session or "user_id" not in session:
        flash("Please log in first.", "danger")
        return redirect(url_for("login"))

    quiz = Quiz.query.get_or_404(quiz_id)
    questions = quiz.questions
    username = session["username"]

    if request.method == "POST":
        total_score = 0
        for question in questions:
            selected_option = request.form.get(f"question_{question.id}")
            if selected_option and int(selected_option) == question.correct_option:
                total_score += 5

        new_score = Score(
            id=generate_custom_id(Score, "SC"), # type: ignore
            quiz_id=quiz.id, # type: ignore
            user_id=session["user_id"], # type: ignore
            total_scored=total_score # type: ignore
        )
        db.session.add(new_score)
        db.session.commit()

        flash(f"You scored {total_score}/{len(questions)}!", "success")
        return redirect(url_for("quiz_summary", username=username, quiz_id=quiz_id))

    return render_template("user/attempt_quiz.html", quiz=quiz, questions=questions, username=username)

@app.route("/user/view_quiz/<quiz_id>")
def view_quiz(quiz_id):
    if "username" not in session:
        flash("Please log in first.", "danger")
        return redirect(url_for("login"))

    quiz = Quiz.query.get_or_404(quiz_id)
    username = session["username"]
    return render_template("user/view_quiz.html", quiz=quiz, username=username)


# ==========================  SCORE MANAGEMENT AND QUIZ RESULT DISPLAY  ==========================

@app.route("/user/quiz_summary/<username>/<quiz_id>")
def quiz_summary(username, quiz_id):
    if "username" not in session or session["username"] != username:
        flash("Unauthorized access!", "danger")
        return redirect(url_for("login"))

    quiz = Quiz.query.get_or_404(quiz_id)
    user_scores = Score.query.filter_by(user_id=session["user_id"], quiz_id=quiz.id).all()

    return render_template("user/quiz_summary.html", quiz=quiz, user_scores=user_scores, username=username)


@app.route("/user/past_attempts/<username>")
def past_attempts(username):
    if "username" not in session or session["username"] != username:
        flash("Unauthorized access!", "danger")
        return redirect(url_for("login"))

    user_scores = Score.query.filter_by(user_id=session["user_id"]).all()
    quizzes = {score.quiz_id: Quiz.query.get(score.quiz_id) for score in user_scores}

    return render_template("user/past_attempts.html", user_scores=user_scores, quizzes=quizzes, username=username)


# ==========================  QUIZ TIME AND DURATION MANAGEMENT  ==========================

@app.route("/user/quiz_time_check/<quiz_id>")
def quiz_time_check(quiz_id):
    if "username" not in session:
        flash("Please log in first.", "danger")
        return redirect(url_for("login"))

    quiz = Quiz.query.get_or_404(quiz_id)
    current_time = datetime.utcnow()

    if current_time > quiz.date_of_quiz:
        flash("This quiz is no longer available.", "warning")
        return redirect(url_for("user_dash", username=session["username"]))

    return redirect(url_for("attempt_quiz", quiz_id=quiz_id))

## ==========================  USER FUNCTIONALITY  ==========================
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


# ==========================  LOGOUT  ==========================
@app.route("/logout")
def logout():
    session.pop("username", None)
    flash("Logged out successfully.", "success")
    return redirect(url_for("login"))


# ==========================  USER MANAGEMENT  ==========================
@app.route("/admin/users")
def users_list():
    users = User.query.all()
    return render_template("admin/users.html", users=users, username=session["username"])

@app.route("/admin/delete_user/<user_id>")
def delete_user(user_id):
    user = User.query.get_or_404(user_id)

    if user.username == "admin":
        return "Admin account cannot be deleted!"

    db.session.delete(user)  # Delete user
    db.session.commit()
    return redirect(url_for("users_list"))


