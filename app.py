from flask import Flask, render_template, request, redirect, url_for, session
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "cloud_education_secret"

# Upload Folder
UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# In-memory storage (for demo)
users = {}
admins = {}
projects = []
enrollments = {}

# ---------------- HOME ----------------
@app.route("/")
def index():
    return render_template("index.html")

# ---------------- ABOUT ----------------
@app.route("/about")
def about():
    return render_template("about.html")

# ---------------- USER SIGNUP ----------------
@app.route("/signup", methods=["GET","POST"])
def signup():
    if request.method == "POST":
        users[request.form["username"]] = request.form["password"]
        return redirect(url_for("login"))
    return render_template("signup.html")

# ---------------- USER LOGIN ----------------
@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        u = request.form["username"]
        p = request.form["password"]

        if u in users and users[u] == p:
            session["user"] = u
            return redirect(url_for("home"))
    return render_template("login.html")

# ---------------- USER DASHBOARD ----------------
@app.route("/home")
def home():
    if "user" not in session:
        return redirect(url_for("login"))

    user = session["user"]
    ids = enrollments.get(user, [])
    my_projects = [p for p in projects if p["id"] in ids]

    return render_template("home.html", username=user, my_projects=my_projects)

# ---------------- PROJECT LIST ----------------
@app.route("/projects")
def projects_list():
    return render_template("projects_list.html", projects=projects)

# ---------------- ENROLL ----------------
@app.route("/enroll/<int:pid>")
def enroll(pid):
    user = session["user"]

    enrollments.setdefault(user, []).append(pid)
    return redirect(url_for("home"))

# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.pop("user",None)
    return redirect(url_for("index"))

# ================= ADMIN =================

# ADMIN SIGNUP
@app.route("/admin/signup", methods=["GET","POST"])
def admin_signup():
    if request.method == "POST":
        admins[request.form["username"]] = request.form["password"]
        return redirect(url_for("admin_login"))
    return render_template("admin_signup.html")

# ADMIN LOGIN
@app.route("/admin/login", methods=["GET","POST"])
def admin_login():
    if request.method == "POST":
        u = request.form["username"]
        p = request.form["password"]

        if u in admins and admins[u] == p:
            session["admin"] = u
            return redirect(url_for("admin_dashboard"))

    return render_template("admin_login.html")

# ADMIN DASHBOARD
@app.route("/admin/logout")
def admin_logout():
    session.pop("admin", None)
    return redirect(url_for("index"))

# ---------------- RUN ----------------
if _name_ == "_main_":
    app.run(debug=True)

# CREATE PROJECT
@app.route("/admin/create-project", methods=["GET","POST"])
def admin_create_project():

    if request.method == "POST":

        img = request.files["image"]
        doc = request.files["document"]

        img_name = secure_filename(img.filename)
        doc_name = secure_filename(doc.filename)

        img.save(os.path.join(UPLOAD_FOLDER,img_name))
        doc.save(os.path.join(UPLOAD_FOLDER,doc_name))

        projects.append({
            "id": len(projects)+1,
            "title": request.form["title"],
            "problem_statement": request.form["problem_statement"],
            "solution_overview": request.form["solution_overview"],
            "image": img_name,
            "document": doc_name
        })

        return redirect(url_for("admin_dashboard"))

    return render_template("admin_create_project.html")

# ADMIN LOGOUT
@app.route("/admin/logout")
def admin_logout():
    session.pop("admin",None)
    return redirect(url_for("index"))

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)

@app.route("/admin_dashboard")
def admin_dashboard():

    projects = []
    users = []
    enrollments = {}

    return render_template(
        "admin_dashboard.html",
        username="Admin",
        projects=projects,
        users=users,
        enrollments=enrollments
    )