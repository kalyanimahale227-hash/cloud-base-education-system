# cloud-base-education-system
**Cloud Based Education System**
This project is a Flask-based Cloud Education System designed to run on AWS Cloud.
It provides an online platform where students can browse projects and enroll, while admins can manage educational projects.
The system uses AWS DynamoDB for database management and AWS SNS for sending notifications.


✅ Features
👩‍🎓 Student Portal
Student Signup
Student Login
Browse Available Projects
Enroll in Projects

👨‍💼 Admin Portal
Admin Signup / Login
Create Educational Projects (with image & document upload)
View Registered Students
Admin Dashboard
☁️ AWS Integration
DynamoDB
Stores:
Students
Admins
Projects
Enrollment Details
SNS (Simple Notification Service)
Sends notifications for:
New Signup
Project Enrollment

🧰 Prerequisites
Python 3.8 or higher
AWS Account (for deployment)
Flask Framework
VS Code (recommended)
⚙ Installation
Step 1: Clone Project
Copy code
Bash
git clone <repository-url>
cd cloud_based_education_system
Step 2: Install Required Libraries
Copy code
Bash
pip install -r requirements.txt

▶ Running Locally
🔹 Simple Local Version (Without AWS)
Copy code
Bash
python app.py
Uses in-memory storage (no cloud).
🔹 AWS Version (Mocked Services)
Copy code
Bash
python test_app_aws.py
Runs DynamoDB + SNS locally using mock services.
Access in browser:
Copy code

http://localhost:5000
⚠ Data will reset when server stops.
🚀 Deployment on AWS EC2
Steps:
Create EC2 instance
Attach IAM Role with:
AmazonDynamoDBFullAccess
AmazonSNSFullAccess
Clone project on EC2
Update in app_aws.py:
