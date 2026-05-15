from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from database import db, User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if User.query.filter_by(username=username).first():
            flash("Username already exists!", "danger")
            return redirect(url_for("auth.signup"))
        hashed_pw = generate_password_hash(password)
        new_user = User(username=username, password=hashed_pw, role="student")
        db.session.add(new_user)
        db.session.commit()
        flash("Registration successful! Please login.", "success")
        return redirect(url_for("auth.login"))
    return render_template("signup.html")

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = User.query.filter_by(username=username, role="student").first()
        if user and check_password_hash(user.password, password):
            session["user_id"] = user.id
            session["username"] = user.username
            flash(f"Welcome back, {user.username}!", "success")
            return redirect(url_for("student.home"))
        flash("Invalid username or password.", "danger")
    return render_template("login.html")

@auth_bp.route("/admin/signup", methods=["GET", "POST"])
def admin_signup():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if User.query.filter_by(username=username).first():
            flash("Admin username already exists!", "danger")
            return redirect(url_for("auth.admin_signup"))
        hashed_pw = generate_password_hash(password)
        new_admin = User(username=username, password=hashed_pw, role="admin")
        db.session.add(new_admin)
        db.session.commit()
        flash("Admin account created! Please login.", "success")
        return redirect(url_for("auth.admin_login"))
    return render_template("admin_signup.html")

@auth_bp.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username, role="admin").first()
        if user and check_password_hash(user.password, password):
            session["admin_id"] = user.id
            session["admin_user"] = user.username
            flash("Admin login successful!", "success")
            return redirect(url_for("faculty.admin_dashboard"))
        flash("Invalid admin credentials.", "danger")
    return render_template("admin_login.html")

@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("Successfully logged out.", "info")
    return redirect(url_for("index"))
