from flask import Flask, render_template, request, redirect, url_for, session, flash
import os
import boto3
import uuid
from werkzeug.utils import secure_filename
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError

app = Flask(__name__)
app.secret_key = 'cloud_edu_secure_key'

# --- AWS Configuration ---
REGION = 'us-east-1' # Change to your region
#SNS_TOPIC_ARN = 'arn:aws:sns:us-east-1:123456789012:MyEduTopic' Replace with your ARN

# Initialize AWS Resources
dynamodb = boto3.resource('dynamodb', region_name=REGION)
sns = boto3.client('sns', region_name=REGION)

# DynamoDB Tables
users_table = dynamodb.Table('Users')
admin_table = dynamodb.Table('AdminUsers')
projects_table = dynamodb.Table('Projects')
enrollments_table = dynamodb.Table('Enrollments')

#SNS Topic ARN(Replace with your actualSNS Topic arn)
SNS_TOPIC_ARN ='arn:aws:sns:us-east-1:911167905203:aws_cloud_education_topic'


# File Upload Config (Local storage on EC2)
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# --- Helper Functions ---
def send_cloud_notification(subject, message):
    """Sends a notification via AWS SNS"""
    try:
        sns.publish(TopicArn=SNS_TOPIC_ARN, Subject=subject, Message=message)
    except ClientError as e:
        print(f"SNS Error: {e}")

# --- Routes ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # DynamoDB Check
        response = users_table.get_item(Key={'username': username})
        if 'Item' in response:
            return "User already exists!"
        
        users_table.put_item(Item={'username': username, 'password': password})
        send_cloud_notification("New Signup", f"User {username} joined the platform.")
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        response = users_table.get_item(Key={'username': username})
        if 'Item' in response and response['Item']['password'] == password:
            session['username'] = username
            return redirect(url_for('home'))
        return "Invalid credentials!"
    return render_template('login.html')

@app.route('/enroll/<project_id>')
def enroll(project_id):
    if 'username' not in session:
        return redirect(url_for('login'))
        
    username = session['username']
    
    # Get current enrollments from DynamoDB
    res = enrollments_table.get_item(Key={'username': username})
    current_ids = res.get('Item', {}).get('project_ids', [])
    
    if project_id not in current_ids:
        current_ids.append(project_id)
        enrollments_table.put_item(Item={'username': username, 'project_ids': current_ids})
        
        # Cloud Notification
        send_cloud_notification("Course Enrollment", f"Student {username} enrolled in Project ID: {project_id}")
        
    return redirect(url_for('home'))

@app.route('/admin/create-project', methods=['GET', 'POST'])
def admin_create_project():
    if 'admin' not in session: return redirect(url_for('admin_login'))
    
    if request.method == 'POST':
        title = request.form['title']
        project_id = str(uuid.uuid4())[:8] # Generate unique cloud ID
        
        # File Handling
        img = request.files['image']
        img_filename = secure_filename(img.filename)
        img.save(os.path.join(app.config['UPLOAD_FOLDER'], img_filename))
        
        # Save to DynamoDB
        projects_table.put_item(Item={
            'id': project_id,
            'title': title,
            'description': request.form['problem_statement'],
            'image': img_filename
        })
        
        return redirect(url_for('admin_dashboard'))
    return render_template('admin_create_project.html')

if __name__ == '__main__':
    # host='0.0.0.0' is required for EC2 to be accessible externally

    app.run(host='0.0.0.0', port=5000, debug=True)

