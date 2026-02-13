from flask import Flask, render_template, request, redirect, url_for, session, flash
import os
import boto3
import uuid
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError

app = Flask(__name__)
app.secret_key = 'cloud_edu_secure_key'

# --- AWS Configuration ---
REGION = 'eu-north-1'   # ⚠️ SAME as your SNS ARN region

# Initialize AWS Resources
dynamodb = boto3.resource('dynamodb', region_name=REGION)
sns = boto3.client('sns', region_name=REGION)

# DynamoDB Tables
users_table = dynamodb.Table('Users')
admin_table = dynamodb.Table('AdminUsers')
projects_table = dynamodb.Table('Projects')
enrollments_table = dynamodb.Table('Enrollments')

# SNS Topic ARN
SNS_TOPIC_ARN = 'arn:aws:sns:eu-north-1:593857178207:aws_cloud_topic'

# File Upload Config
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# --- Helper Function ---
def send_cloud_notification(subject, message):
    try:
        sns.publish(
            TopicArn=SNS_TOPIC_ARN,
            Subject=subject,
            Message=message
        )
    except ClientError as e:
        print(f"SNS Error: {e}")

# ---------------- ROUTES ---------------- #

@app.route('/')
def index():
    return render_template('index.html')

# ---------------- USER SIGNUP ---------------- #

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        response = users_table.get_item(Key={'username': username})
        if 'Item' in response:
            return "User already exists!", 400

        hashed_password = generate_password_hash(password)

        users_table.put_item(Item={
            'username': username,
            'password': hashed_password
        })

        send_cloud_notification("New Signup", f"User {username} joined.")

        return redirect(url_for('login'))

    return render_template('signup.html')

# ---------------- USER LOGIN ---------------- #

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        response = users_table.get_item(Key={'username': username})

        if 'Item' in response:
            stored_password = response['Item']['password']

            if check_password_hash(stored_password, password):
                session['username'] = username
                return redirect(url_for('home'))

        return "Invalid credentials!"

    return render_template('login.html')

# ---------------- HOME ---------------- #

@app.route('/home')
def home():
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']

    response = enrollments_table.get_item(Key={'username': username})
    project_ids = response.get('Item', {}).get('project_ids', [])

    my_projects = []

    for pid in project_ids:
        res = projects_table.get_item(Key={'id': pid})
        if 'Item' in res:
            my_projects.append(res['Item'])

    return render_template('home.html', username=username, my_projects=my_projects)

# ---------------- ENROLL ---------------- #

@app.route('/enroll/<project_id>')
def enroll(project_id):
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']

    response = enrollments_table.get_item(Key={'username': username})
    current_ids = response.get('Item', {}).get('project_ids', [])

    if project_id not in current_ids:
        current_ids.append(project_id)

        enrollments_table.put_item(Item={
            'username': username,
            'project_ids': current_ids
        })

        send_cloud_notification(
            "Course Enrollment",
            f"Student {username} enrolled in Project ID: {project_id}"
        )

    return redirect(url_for('home'))

# ---------------- ADMIN CREATE PROJECT ---------------- #

@app.route('/admin/create-project', methods=['GET', 'POST'])
def admin_create_project():
    if 'admin' not in session:
        return redirect(url_for('admin_login'))

    if request.method == 'POST':
        title = request.form['title']
        problem_statement = request.form['problem_statement']

        project_id = str(uuid.uuid4())[:8]

        image = request.files['image']
        image_filename = None

        if image:
            image_filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))

        projects_table.put_item(Item={
            'id': project_id,
            'title': title,
            'description': problem_statement,
            'image': image_filename
        })

        send_cloud_notification(
            "New Project",
            f"Project '{title}' created successfully."
        )

        return redirect(url_for('admin_dashboard'))

    return render_template('admin_create_project.html')

# ---------------- RUN APP ---------------- #

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)



