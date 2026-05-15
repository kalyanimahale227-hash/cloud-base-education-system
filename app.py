from flask import Flask, render_template
import os
from dotenv import load_dotenv
from config import Config
from database import db, init_db

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "cloud_education_secret_key_v1")
app.config["SQLALCHEMY_DATABASE_URI"] = Config.SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# ---------------- CONFIG ----------------
UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize Database
init_db(app)

# ---------------- REGISTER BLUEPRINTS ----------------
from routes.auth import auth_bp
from routes.student import student_bp
from routes.faculty import faculty_bp

app.register_blueprint(auth_bp)
app.register_blueprint(student_bp)
app.register_blueprint(faculty_bp)

# ---------------- BASE ROUTES ----------------
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

# ================= RUN APP =================
if __name__ == "__main__":
    # Ensure port 5000 is open for local dev
    app.run(host='0.0.0.0', port=5000, debug=True)