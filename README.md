# Quiz-master-v1
This is a mad-1 quiz master project for jan25 term.

# Quiz Master Project

## 📄 Project Overview

Quiz Master is an interactive web application that allows users to test their knowledge by attempting quizzes, track their scores, and view insightful performance summaries. Admins can manage subjects, chapters, quizzes, and users, while also accessing analytical dashboards.

---

## 🛠️ Technologies Used

- **Python** (Flask)
- **SQLAlchemy** (Database ORM)
- **SQLite** (Database)
- **Bootstrap** (Frontend styling)
- **Chart.js & Matplotlib** (Data visualization)

---

## 🔥 Common Log Issues and Resolutions

### 1️. Login Issues: User does not exist

Error:

```
flash("User does not exist.", "danger")
```

**Cause:** Incorrect condition check after querying user.
**Resolution:** Ensure you return after rendering the template.

```python
if not this_user:
    flash("User does not exist.", "danger")
    return render_template("login.html")
```

---

### 2️. **IntegrityError when Registering a User**

**Error:**

```
sqlalchemy.exc.IntegrityError: UNIQUE constraint failed: user.id
```

**Cause:** `generate_custom_id()` returned an already-existing ID.
**Resolution:** Ensure ID generation checks for existing records:


---

### 3️. **Delete Admin Error: IntegrityError**

**Error:**

```
sqlalchemy.exc.IntegrityError: NOT NULL constraint failed: score.user_id
```

**Cause:** Scores were not deleted when a user was deleted.
**Resolution:** Add cascading deletes or manually clean related data:

```python
Score.query.filter_by(user_id=user.id).delete()
db.session.delete(user)
db.session.commit()
```

---

### 4️. **Quiz Summary Charts Not Working (JSON Error)**

**Error:**

```
TypeError: Object of type Undefined is not JSON serializable
```

**Cause:** Missing or null data passed to `tojson` in Jinja.
**Resolution:** Ensure null checks:

```python
bar_chart_data = bar_chart_data or []
return render_template('admin/admin_summary.html', bar_chart_data=bar_chart_data)
```

---

### 5️. **Search Function Redirecting Admin to User Dashboard**

**Cause:** Incorrect redirect without checking user type.
**Resolution:** Ensure user type is correctly handled:

```python
if user_type == 'admin':
    return redirect(url_for('admin_dash', username=username))
else:
    return redirect(url_for('user_dash', username=username))
```

---

## 💡 **Contributing**

-  Some Git command to interact with repository.
- Create a new branch (`feature/your-feature-name`).
- Initialize git (`git init`)
- add new changes (`git add <file name>`)
- Commit changes (`git commit -m 'Add your feature'`).
- Push to the branch (`git push origin your-branch`).
- Create a pull request.

---

## Project Collaboration & Development
This project, Quiz Master, was developed by me as part of my web application coursework.

Throughout the development process, I used AI-powered collaboration to:

- Debug errors in Flask routes and models.
- Structure key functionalities like user authentication, search features, and data visualization.
- Optimize backend logic for quiz scoring, summaries, and API integration.
- Enhance design by suggesting modern layouts and interactivity.

All AI-assisted code was carefully reviewed, tested, and customized to fit the specific needs of the Quiz Master application. The final product reflects both AI support and my own logic, creativity, and coding efforts.

## 📧 **Contact**

For any queries, feel free to reach out via [23f3001252@ds.study.iitm.ac.in](mailto\\23f3001252@ds.study.iitm.ac.in)

