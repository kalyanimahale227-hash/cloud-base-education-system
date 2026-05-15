from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app
import os
from werkzeug.utils import secure_filename
from database import db, User, Project, Enrollment, Submission, Material, Notification, Quiz
from config import Config
import dynamo as dynamo_db
from routes.utils import admin_required, allowed_file

faculty_bp = Blueprint('faculty', __name__)

@faculty_bp.route("/admin_dashboard")
@admin_required
def admin_dashboard():
    projects = Project.query.all()
    users = User.query.filter_by(role="student").all()
    total_enrollments = Enrollment.query.count()
    return render_template("admin_dashboard.html", username=session["admin_user"], projects=projects, users=users, total_enrollments=total_enrollments)

@faculty_bp.route("/admin/create-project", methods=["GET", "POST"])
@admin_required
def admin_create_project():
    if request.method == "POST":
        title = request.form["title"]
        problem = request.form["problem_statement"]
        solution = request.form["solution_overview"]
        img = request.files.get("image")
        doc = request.files.get("document")
        img_name = secure_filename(img.filename) if img and allowed_file(img.filename) else None
        doc_name = secure_filename(doc.filename) if doc and allowed_file(doc.filename) else None
        if img_name:
            img.save(os.path.join(current_app.config["UPLOAD_FOLDER"], img_name))
        if doc_name:
            doc.save(os.path.join(current_app.config["UPLOAD_FOLDER"], doc_name))
        new_project = Project(title=title, problem_statement=problem, solution_overview=solution, image=img_name, document=doc_name)
        db.session.add(new_project)
        db.session.commit()
        flash("Project created successfully!", "success")
        return redirect(url_for("faculty.admin_dashboard"))
    return render_template("admin_create_project.html")

@faculty_bp.route("/admin/add-material/<int:pid>", methods=["GET", "POST"])
@admin_required
def admin_add_material(pid):
    project = Project.query.get_or_404(pid)
    if request.method == "POST":
        name = request.form["material_name"]
        file = request.files.get("material_file")
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
            file.save(file_path)
            if Config.USE_AWS:
                try:
                    dynamo_db.add_material_to_course(course_id=str(pid), material_link=file_path, material_name=name)
                    flash("Material added to Cloud (DynamoDB)!", "success")
                except Exception as e:
                    flash(f"Cloud sync failed: {str(e)}", "danger")
            else:
                new_material = Material(project_id=pid, name=name, link=file_path)
                db.session.add(new_material)
                db.session.commit()
                flash("Material added successfully (SQLite)!", "success")
            return redirect(url_for("faculty.admin_dashboard"))
    return render_template("add_material.html", project=project)

@faculty_bp.route("/admin/submissions")
@admin_required
def admin_submissions_list():
    submissions = Submission.query.order_by(Submission.submitted_at.desc()).all()
    return render_template("admin_view_submissions.html", submissions=submissions)

@faculty_bp.route("/admin/grade/<int:sid>", methods=["GET", "POST"])
@admin_required
def admin_grade_submission(sid):
    submission = Submission.query.get_or_404(sid)
    if request.method == "POST":
        grade = request.form["grade"]
        feedback = request.form["feedback"]
        msg = f"Your project '{submission.project.title}' has been graded: {grade}/100"
        if Config.USE_AWS:
            try:
                dynamo_db.grade_submission(submission_id=str(sid), grade=int(grade), feedback=feedback, student_id=str(submission.student_id))
                flash("Grade updated in Cloud (DynamoDB)!", "success")
            except Exception as e:
                flash(f"Cloud sync failed: {str(e)}", "danger")
        else:
            submission.grade = int(grade)
            submission.feedback = feedback
            notif = Notification(user_id=submission.student_id, message=msg)
            db.session.add(notif)
            db.session.commit()
            flash("Submission graded and student notified!", "success")
        return redirect(url_for("faculty.admin_submissions_list"))
    return render_template("admin_grade_form.html", submission=submission)

@faculty_bp.route("/admin/create-quiz/<int:pid>", methods=["GET", "POST"])
@admin_required
def admin_create_quiz(pid):
    project = Project.query.get_or_404(pid)
    if request.method == "POST":
        title = request.form["quiz_title"]
        questions = [{"text": request.form["q1_text"], "a": request.form["q1_a"], "b": request.form["q1_b"], "c": request.form["q1_c"], "d": request.form["q1_d"], "ans": request.form["q1_ans"].upper()}]
        if Config.USE_AWS:
            try:
                dynamo_db.create_quiz(course_id=str(pid), faculty_id=str(session["admin_id"]), title=title, questions=questions)
                flash("Quiz published to Cloud (DynamoDB)!", "success")
            except Exception as e:
                flash(f"Cloud sync failed: {str(e)}", "danger")
        else:
            new_quiz = Quiz(project_id=pid, title=title, questions=questions)
            db.session.add(new_quiz)
            db.session.commit()
            flash("Quiz created successfully (SQLite)!", "success")
        return redirect(url_for("faculty.admin_dashboard"))
    return render_template("admin_create_quiz.html", project=project)
