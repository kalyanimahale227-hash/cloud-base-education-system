from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app
import os
from werkzeug.utils import secure_filename
from database import db, User, Project, Enrollment, Submission, Notification, Quiz
from config import Config
import dynamo as dynamo_db
from routes.utils import login_required, allowed_file

student_bp = Blueprint('student', __name__)

@student_bp.route("/home")
@login_required
def home():
    user = User.query.get(session["user_id"])
    my_enrollments = Enrollment.query.filter_by(user_id=user.id).all()
    my_projects = [Project.query.get(e.project_id) for e in my_enrollments]
    all_projects = Project.query.all()
    notifications = Notification.query.filter_by(user_id=user.id).order_by(Notification.created_at.desc()).all()
    return render_template("student_dashboard.html", username=user.username, my_projects=my_projects, projects=all_projects, notifications=notifications)

@student_bp.route("/projects")
def projects_list():
    projects = Project.query.all()
    return render_template("projectlist.html", projects=projects)

@student_bp.route("/enroll/<int:pid>")
@login_required
def enroll(pid):
    user_id = session["user_id"]
    existing = Enrollment.query.filter_by(user_id=user_id, project_id=pid).first()
    if not existing:
        new_enroll = Enrollment(user_id=user_id, project_id=pid)
        db.session.add(new_enroll)
        db.session.commit()
        flash("Successfully enrolled in project!", "success")
    else:
        flash("You are already enrolled in this project.", "info")
    return redirect(url_for("student.home"))

@student_bp.route("/submit/<int:pid>", methods=["GET", "POST"])
@login_required
def submit_project(pid):
    user_id = session["user_id"]
    project = Project.query.get_or_404(pid)
    enrollment = Enrollment.query.filter_by(user_id=user_id, project_id=pid).first()
    if not enrollment:
        flash("You must be enrolled in this project to submit work.", "warning")
        return redirect(url_for("student.home"))

    if request.method == "POST":
        file = request.files.get("submission_file")
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
            file.save(file_path)
            if Config.USE_AWS:
                try:
                    dynamo_db.submit_project(student_id=str(user_id), course_id=str(pid), filename=filename, s3_url=file_path)
                    flash("Project submitted successfully to Cloud (DynamoDB)!", "success")
                except Exception as e:
                    flash(f"Cloud submission failed: {str(e)}", "danger")
            else:
                new_submission = Submission(student_id=user_id, project_id=pid, filename=filename, s3_url=file_path)
                db.session.add(new_submission)
                db.session.commit()
                flash("Project submitted successfully (SQLite)!", "success")
            return redirect(url_for("student.home"))
        else:
            flash("Invalid file format. Please upload PDF or Image.", "danger")
    return render_template("submit_project.html", project=project)

@student_bp.route("/quiz/take/<int:qid>", methods=["GET", "POST"])
@login_required
def take_quiz(qid):
    quiz = Quiz.query.get_or_404(qid)
    if request.method == "POST":
        score = 0
        total = len(quiz.questions)
        for idx, q in enumerate(quiz.questions):
            ans = request.form.get(f"q{idx+1}")
            if ans == q["ans"]:
                score += 1
        final_score = int((score / total) * 100)
        msg = f"You scored {final_score}% on the quiz: {quiz.title}"
        notif = Notification(user_id=session["user_id"], message=msg)
        db.session.add(notif)
        db.session.commit()
        flash(f"Quiz submitted! Your score: {final_score}%", "success")
        return redirect(url_for("student.home"))
    return render_template("take_quiz.html", quiz=quiz, questions=quiz.questions)
