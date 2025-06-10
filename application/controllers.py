from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from sqlalchemy.exc import IntegrityError
from functools import wraps
from sqlalchemy import func
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
                session["type"] = "admin" if this_user.username == "admin" else "user"

                flash("Logged in successfully.", "success")

                if this_user.username == "admin":
                    return redirect(url_for('admin_dash', username=username))
                else:
                    return redirect(url_for('user_dash', username=username))
            else:
                flash("Incorrect password.", "danger")
                render_template("login.html")
        else:
            flash("User does not exist.", "danger")
            render_template("login.html")
    return render_template('login.html')

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get('name')
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if not name or not username or not password or not confirm_password:
            flash("Please fill out all fields.", "warning")
            render_template("register.html")
        
        if password != confirm_password:
            flash("Passwords do not match", "danger")
            render_template("register.html")
        
        # Check if username already exists
        user = User.query.filter_by(username=username).first()
        if user:
            flash("Username already exists.", "danger")
            return render_template("register.html")

        try:
            hashed_password = generate_password_hash(password) # type: ignore
            new_user = User(id=generate_custom_id(User, "US"), name=name, username=username, password_hash=hashed_password # type: ignore
            )
            db.session.add(new_user)
            db.session.commit()

            flash("You are successfully registered!", "success")
            return redirect(url_for('login'))

        except IntegrityError:
            db.session.rollback()  # Prevent broken transactions
            flash("Something went wrong. Please try again.", "danger")
            return render_template("register.html")
    
    return render_template('register.html')

# =========================== CHECK AUTHENTICATION ======================

#Both admin and user authentication decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "username" not in session:
            flash("Please log in to access this page.", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

# Admin authentication decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "username" not in session or session.get("type") != "admin":
            flash("Access denied! Admin only.", "danger")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

# User authentication decorator
def user_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "username" not in session or session.get("type") != "user":
            flash("Access denied! User only.", "danger")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function


# ==========================  ADMIN DASHBOARD  ==========================

@app.route("/admin/dashboard/<username>")
@admin_required
def admin_dash(username):
    subjects = Subject.query.all()
    chapters = Chapter.query.all()

    # Get count of questions for each chapter
    chapter_question_counts = db.session.query(
        Chapter.id,
        func.count(Question.id).label('question_count')
    ).join(Quiz, Chapter.id == Quiz.chapter_id)\
     .outerjoin(Question, Quiz.id == Question.quiz_id)\
     .group_by(Chapter.id).all()

    # Convert to a dictionary for easy lookup in template
    chapter_question_map = {chapter_id: count for chapter_id, count in chapter_question_counts}

    return render_template(
        "admin/admin_dash.html",
        username=username,
        subjects=subjects,
        chapters=chapters,
        chapter_question_map=chapter_question_map
    )

# ==========================  SUBJECT MANAGEMENT  ==========================

@app.route("/admin/add_subject/<username>", methods=["GET", "POST"])
@admin_required
def add_subject(username):
    if request.method == "POST":
        name = request.form.get("subject_name")
        description = request.form.get("subject_desc")
        
        if Subject.query.filter_by(name=name).first():
            flash("Subject already exists.", "danger")
            return redirect(url_for("admin_dash", username=session["username"]))

        new_subject = Subject(id=generate_custom_id(Subject, "SB"), name=name, description=description) # type: ignore
        db.session.add(new_subject)
        db.session.commit()
        flash("Subject added successfully!", "success")
        return redirect(url_for("admin_dash", username=username))
    
    return render_template("admin/add_subject.html", username=username)

@app.route("/admin/edit_subject/<subject_id>", methods=["GET", "POST"])
@admin_required
def edit_subject(subject_id):
    subject = Subject.query.get_or_404(subject_id)

    if request.method == "POST":
        subject.name = request.form.get("subject_name")
        subject.description = request.form.get("subject_desc")

        db.session.commit()
        flash("Subject edited successfully!", "success")
        return redirect(url_for("admin_dash", username=session["username"]))

    return render_template("admin/edit_subject.html", subject=subject, username=session["username"])

@app.route("/admin/delete_subject/<subject_id>")
@admin_required
def delete_subject(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    Chapter.query.filter_by(subject_id=subject.id).delete()
    db.session.delete(subject)
    db.session.commit()
    flash("subject deleted successfully!", "success")
    return redirect(url_for("admin_dash", username=session["username"]))


# ==========================  CHAPTER MANAGEMENT  ==========================

@app.route("/admin/add_chapter/<username>", methods=["GET", "POST"])
@admin_required
def add_chapter(username):
    if request.method == "POST":
        chapter_name = request.form.get("chapter_name")
        subject_name = request.form.get("subject_name")
        description = request.form.get("chapter_desc")

        subject = Subject.query.filter_by(name=subject_name).first() # type: ignore
        if not subject:
            flash("Subject not found! Please add the subject first.", "danger")
            return render_template("admin/add_chapter.html", username=username)
        
        chapter = Chapter.query.filter_by(name=chapter_name, subject_id=subject.id).first()
        if chapter :
            flash("Chapter already exist.", "danger")
            return render_template("admin/add_chapter.html", username=username)
        
        new_chapter = Chapter(id=generate_custom_id(Chapter, "CH"), name=chapter_name, description=description, subject_id=subject.id) # type: ignore
        db.session.add(new_chapter)
        db.session.commit()
        flash("Chapter added successfully!", "success")
        return redirect(url_for("admin_dash", username=username))
    
    return render_template("admin/add_chapter.html", username=username)

@app.route("/admin/edit_chapter/<chapter_id>", methods=["GET", "POST"])
@admin_required
def edit_chapter(chapter_id):
    chapter = Chapter.query.get_or_404(chapter_id)
    subject = Subject.query.get_or_404(chapter.subject_id)

    if request.method == "POST":
        name = request.form.get("chapter_name")
        chapter.name = request.form.get("chapter_name")
        chapter.description = request.form.get("chapter_desc")

        db.session.commit()
        flash("Chapter edited successfully!", "success")
        return redirect(url_for("admin_dash", username=session["username"]))

    return render_template("admin/edit_chapter.html", chapter=chapter, subject=subject, username=session["username"])

@app.route("/admin/delete_chapter/<chapter_id>")
@admin_required
def delete_chapter(chapter_id):
    chapter = Chapter.query.get_or_404(chapter_id)
    Quiz.query.filter_by(chapter_id=chapter.id).delete()

    db.session.delete(chapter)
    db.session.commit()
    flash("Chapter deleted successfully!", "info")
    return redirect(url_for("admin_dash", username=session["username"]))

# ==========================  QUIZ MANAGEMENT  ==========================

@app.route("/admin/quiz_management")
@admin_required
def quiz_management():
    quizzes = Quiz.query.all()
    return render_template("admin/quiz_mng.html", username=session["username"], quizzes=quizzes)

@app.route("/admin/quiz_management/add_quiz", methods=["GET", "POST"])
@admin_required
def add_quiz():
    if request.method == "POST":
        title = request.form.get("title")
        chapter_id = request.form.get("chapter_id")
        duration = request.form.get("duration")
        quiz_date = datetime.strptime(request.form.get("date"), "%Y-%m-%d") # type: ignore

        Check_chapter = Chapter.query.filter_by(id=chapter_id).first() 
        if not Check_chapter :
            flash("Chapter is not available. Create chapter first!", "danger")
            return redirect(url_for("quiz_management", username=session["username"]))
        
        check_quiz = Quiz.query.filter_by(title=title).first()
        if check_quiz:
            flash("Quiz has alredy exist.", "danger")
            return redirect(url_for("quiz_management", username=session["username"]))
        
        new_quiz = Quiz(id=generate_custom_id(Quiz, "QZ"), title=title, chapter_id=chapter_id, time_duration=duration, date_of_quiz=quiz_date) # type: ignore
        db.session.add(new_quiz)
        db.session.commit()
        flash("Quiz added successfully!", "success")
        return redirect(url_for("quiz_management", username=session["username"]))

    chapters = Chapter.query.all()
    return render_template("admin/add_quiz.html", username=session["username"], chapters=chapters)

@app.route("/admin/quiz_management/edit_quiz/<quiz_id>", methods=["GET", "POST"])
@admin_required
def edit_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)

    if request.method == "POST":
        quiz.title = request.form.get("title")
        quiz.chapter_id = request.form.get("chapter_id")
        quiz.time_duration = request.form.get("duration")
        quiz.date_of_quiz = datetime.strptime(request.form.get("date"), "%Y-%m-%d") # type: ignore

        Check_chapter = Chapter.query.filter_by(id=quiz.chapter_id).first() 
        if not Check_chapter :
            flash("Quiz is not available for this chapter. Create chapter first!", "danger")
            return redirect(url_for("quiz_management", username=session["username"]))
        
        db.session.commit()
        flash("Quiz updated successfully!", "success")
        return redirect(url_for("quiz_management", username=session["username"]))

    return render_template("admin/edit_quiz.html", username=session["username"], quiz=quiz)

@app.route("/admin/quiz_management/delete_quiz/<quiz_id>")
@admin_required
def delete_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)

    Question.query.filter_by(quiz_id=quiz.id).delete()
    Score.query.filter_by(quiz_id=quiz_id).delete()
    db.session.delete(quiz)
    db.session.commit()
    flash("Quiz deleted successfully!", "success")
    return redirect(url_for("quiz_management", username=session["username"]))

@app.route("/admin/quiz_management/add_question", methods=["GET", "POST"])
@admin_required
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
        question_statement=request.form.get("question_statement")
        Check_question = Question.query.filter_by(question_statement=question_statement).first()  # type: ignore
        if Check_question :
            flash("Question already available for this quiz.", "danger")
            return redirect(url_for("quiz_management", username=session["username"]))
   
        db.session.add(new_question)
        db.session.commit()
        flash("Question added successfully!", "success")
        return redirect(url_for("quiz_management", username=session["username"]))

    quizzes = Quiz.query.all()
    return render_template("admin/add_question.html", username=session["username"], quizzes=quizzes)


@app.route("/admin/quiz_management/edit_question/<question_id>", methods=["GET", "POST"])
@admin_required
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
@admin_required
def delete_question(question_id):
    question = Question.query.get_or_404(question_id)
    db.session.delete(question)
    db.session.commit()
    flash("Question deleted successfully!", "success")
    return redirect(url_for("quiz_management"))

# ==========================  ADMIN SCORE MANAGEMENT  ==========================

@app.route("/admin/cleanup_scores")
@admin_required
def cleanup_orphan():
     # Find and delete all quizzes linked to deleted Chapter
    quizzes = Quiz.query.all()
    for quiz in quizzes:
        if quiz.chapter is None:  # If chapter no longer exists
            db.session.delete(quiz)

    # Find and delete all scores linked to deleted quizzes
    scores = Score.query.all()
    for score in scores:
        if score.quiz is None:  # If quiz no longer exists
            db.session.delete(score)

    # Find and delete all questions linked to deleted quizzes
    questions = Question.query.all()
    for question in questions:
        if question.quiz is None:
            db.session.delete(question)

    db.session.commit()
    flash("delete all quizzes, questions and scores linked to deleted chapter", "success")
    return redirect(url_for("admin_dash", username=session["username"]))


@app.route('/admin_summary/<username>')
@admin_required
def admin_summary(username):

    # Top scores for bar chart
    top_scores = db.session.query(
        Subject.name,
        func.coalesce(func.max(Score.total_scored), 0).label('max_score')
    ).join(Chapter, Subject.id == Chapter.subject_id)\
     .join(Quiz, Chapter.id == Quiz.chapter_id)\
     .outerjoin(Score, Quiz.id == Score.quiz_id)\
     .group_by(Subject.name).all()

    bar_chart_data = [{"subject": subject or "Unknown", "score": score or 0} for subject, score in top_scores]

    # User attempts for pie chart
    user_attempts = db.session.query(
        Subject.name,
        func.count(Score.id).label('attempt_count')
    ).join(Chapter, Subject.id == Chapter.subject_id)\
     .join(Quiz, Chapter.id == Quiz.chapter_id)\
     .join(Score, Quiz.id == Score.quiz_id)\
     .group_by(Subject.name).all()

    pie_chart_data = [{"subject": subject or "Unknown", "count": count or 0} for subject, count in user_attempts]

    return render_template(
        'admin/admin_summary.html',username=username,
        bar_chart_data=bar_chart_data or [],
        pie_chart_data=pie_chart_data or []
    )


# ==========================  USER DASHBOARD AND QUIZ ATTEMPT  ==========================

@app.route("/user/dashboard/<username>")
@user_required
def user_dash(username):
    subjects = Subject.query.all()
    quizzes = Quiz.query.all()
    return render_template("user/user_dash.html", username=username, subjects=subjects, quizzes=quizzes)


@app.route("/user/attempt_quiz/<quiz_id>", methods=["GET", "POST"])
@user_required
def attempt_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = quiz.questions
    username = session["username"]
    duration = int(quiz.time_duration.split(":")[0]) * 60 + int(quiz.time_duration.split(":")[1])
    
    if request.method == "POST":
        start_time = datetime.strptime(session.get("start_time"), "%Y-%m-%d %H:%M:%S") # type: ignore
        end_time = start_time + timedelta(seconds=duration)
        
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

        flash(f"You have successfully attempted your quiz. You scored {total_score}/{len(questions)*5}!", "info")
        return redirect(url_for("user_dash", username=username, quiz_id=quiz_id))

    session["start_time"] = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    return render_template("user/attempt_quiz.html", quiz=quiz, questions=questions, duration=duration, username=session["username"])


@app.route("/user/view_quiz/<quiz_id>")
@user_required
def view_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    username = session["username"]
    return render_template("user/view_quiz.html", quiz=quiz, username=username)

@app.route("/user/quiz_score/<username>")
@user_required
def quiz_score(username):
    user_id = session["user_id"]
    scores = Score.query.filter_by(user_id=user_id).all()

    return render_template("user/quiz_score.html", username=username, scores=scores) # type: ignore

# ==========================  SCORE MANAGEMENT AND QUIZ RESULT DISPLAY  ==========================

@app.route('/user/quiz_summary/<username>')
@user_required
def quiz_summary(username):
    user_id = session.get('user_id')

    # Fetch user's quiz attempts and scores
    user_scores = Score.query.filter_by(user_id=user_id).all()

    # Count quizzes by subject
    subject_counts = db.session.query(
        Subject.name,
        db.func.count(Score.quiz_id).label('quiz_count')
    ).join(Chapter, Subject.id == Chapter.subject_id)\
     .join(Quiz, Chapter.id == Quiz.chapter_id)\
     .join(Score, Quiz.id == Score.quiz_id)\
     .filter(Score.user_id == user_id)\
     .group_by(Subject.name).all()

    # Ensure subject data is structured correctly for charts
    subject_data = [{"subject": subject, "count": count} for subject, count in subject_counts]

    # Count quizzes by month
    month_counts = db.session.query(
        db.func.strftime('%m-%Y', Quiz.date_of_quiz).label('month'),
        db.func.count(Score.quiz_id).label('quiz_count')
    ).join(Score, Quiz.id == Score.quiz_id)\
     .filter(Score.user_id == user_id)\
     .group_by('month').all()

    # Ensure month data is structured correctly for charts
    month_data = [{"month": month, "count": count} for month, count in month_counts]

    return render_template('user/quiz_summary.html', 
                           username=username,
                           subject_data=subject_data,
                           month_data=month_data)


# ==========================  QUIZ TIME AND DURATION MANAGEMENT  ==========================

@app.route("/user/quiz_time_check/<quiz_id>")
@user_required
def quiz_time_check(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    current_time = datetime.utcnow()

    # Convert quiz.date_of_quiz (date) to datetime for comparison
    quiz_datetime = datetime.combine(quiz.date_of_quiz, datetime.min.time())

    if current_time > quiz_datetime:  #quiz date with a time of 00:00:00,so both sides use datetime not only date().
        flash("Timeline is over! This quiz is no longer available.", "warning")
        return redirect(url_for("user_dash", username=session["username"], quiz_id=quiz_id))

    return redirect(url_for("attempt_quiz", quiz_id=quiz_id))

# ==========================  LOGOUT  ==========================
@app.route("/logout")
@login_required
def logout():
    session.pop("username", None)
    flash("Logged out successfully.", "success")
    return redirect(url_for("login"))

# ==========================  USER MANAGEMENT  ==========================
@app.route("/admin/users")
@admin_required
def users_list():
    users = User.query.all()
    return render_template("admin/users.html", users=users, username=session["username"])

@app.route("/admin/delete_user/<user_id>")
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)

    if user.username == "admin":
        flash("Admin account cannot be deleted!", "danger")
        return redirect(url_for("users_list"))

    # Delete all related scores first
    Score.query.filter_by(user_id=user.id).delete()

    # Now delete the user
    db.session.delete(user)
    db.session.commit()

    flash("User deleted successfully!", "success")
    return redirect(url_for("users_list"))


# =========================== SEARCH FUNCTIONALITY ======================== #

@app.route('/search', methods=['GET'])
@login_required
def search():
    if 'username' not in session:
        flash("Please log in to access this feature.", "danger")
        return redirect(url_for('login'))

    query = request.args.get('q', '').strip()
    user_type = session["username"]

    user_results, subject_results, quiz_results, question_results = [], [], [], []

    if query:
        search_query = f"%{query}%"

        if user_type == 'admin':
            user_results = User.query.filter((User.username.ilike(search_query)) | (User.name.ilike(search_query))).all()
            subject_results = Subject.query.filter(Subject.name.ilike(search_query)).all()
            quiz_results = Quiz.query.filter(Quiz.title.ilike(search_query)).all()
            question_results = Question.query.filter(Question.question_statement.ilike(search_query)).all()
        else:
            subject_results = Subject.query.filter(Subject.name.ilike(search_query)).all()
            quiz_results = Quiz.query.filter(Quiz.title.ilike(search_query)).all()

    return render_template('search_results.html',
                           query=query,
                           user_results=user_results,
                           subject_results=subject_results,
                           quiz_results=quiz_results,
                           question_results=question_results,
                           user_type=user_type,
                           username=session.get('username'))

