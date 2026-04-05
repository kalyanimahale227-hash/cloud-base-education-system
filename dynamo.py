import boto3
import uuid
from datetime import datetime
from config import Config

dynamodb = boto3.resource(
    'dynamodb',
    region_name=Config.AWS_REGION,
    aws_access_key_id=Config.AWS_ACCESS_KEY,
    aws_secret_access_key=Config.AWS_SECRET_KEY
)

# ─────────────────────────────────────────────
# TABLE REFERENCES
# ─────────────────────────────────────────────
users_table         = dynamodb.Table(Config.USERS_TABLE)
courses_table       = dynamodb.Table(Config.COURSES_TABLE)
submissions_table   = dynamodb.Table(Config.SUBMISSIONS_TABLE)
notifications_table = dynamodb.Table(Config.NOTIFICATIONS_TABLE)
quizzes_table       = dynamodb.Table(Config.QUIZZES_TABLE)


# ─────────────────────────────────────────────
# USER OPERATIONS
# ─────────────────────────────────────────────
def create_user(name, email, password_hash, role):
    """role: 'student' or 'faculty'"""
    user_id = str(uuid.uuid4())
    users_table.put_item(Item={
        'user_id': user_id,
        'name': name,
        'email': email,
        'password': password_hash,
        'role': role,
        'enrolled_courses': [],
        'created_at': datetime.utcnow().isoformat()
    })
    return user_id

def get_user_by_email(email):
    response = users_table.scan(
        FilterExpression='email = :e',
        ExpressionAttributeValues={':e': email}
    )
    items = response.get('Items', [])
    return items[0] if items else None

def get_user_by_id(user_id):
    response = users_table.get_item(Key={'user_id': user_id})
    return response.get('Item')

def enroll_student(user_id, course_id):
    user = get_user_by_id(user_id)
    enrolled = user.get('enrolled_courses', [])
    if course_id not in enrolled:
        enrolled.append(course_id)
        users_table.update_item(
            Key={'user_id': user_id},
            UpdateExpression='SET enrolled_courses = :c',
            ExpressionAttributeValues={':c': enrolled}
        )


# ─────────────────────────────────────────────
# COURSE OPERATIONS
# ─────────────────────────────────────────────
def create_course(title, description, faculty_id):
    course_id = str(uuid.uuid4())
    courses_table.put_item(Item={
        'course_id': course_id,
        'title': title,
        'description': description,
        'faculty_id': faculty_id,
        'materials': [],
        'created_at': datetime.utcnow().isoformat()
    })
    return course_id

def get_all_courses():
    response = courses_table.scan()
    return response.get('Items', [])

def get_course_by_id(course_id):
    response = courses_table.get_item(Key={'course_id': course_id})
    return response.get('Item')

def get_faculty_courses(faculty_id):
    response = courses_table.scan(
        FilterExpression='faculty_id = :f',
        ExpressionAttributeValues={':f': faculty_id}
    )
    return response.get('Items', [])

def add_material_to_course(course_id, material_link, material_name):
    course = get_course_by_id(course_id)
    materials = course.get('materials', [])
    materials.append({
        'name': material_name,
        'link': material_link,
        'uploaded_at': datetime.utcnow().isoformat()
    })
    courses_table.update_item(
        Key={'course_id': course_id},
        UpdateExpression='SET materials = :m',
        ExpressionAttributeValues={':m': materials}
    )


# ─────────────────────────────────────────────
# SUBMISSION OPERATIONS
# ─────────────────────────────────────────────
def submit_project(student_id, course_id, filename, s3_url):
    sub_id = str(uuid.uuid4())
    submissions_table.put_item(Item={
        'submission_id': sub_id,
        'student_id': student_id,
        'course_id': course_id,
        'filename': filename,
        's3_url': s3_url,
        'grade': None,
        'feedback': None,
        'submitted_at': datetime.utcnow().isoformat()
    })
    return sub_id

def get_submissions_by_course(course_id):
    response = submissions_table.scan(
        FilterExpression='course_id = :c',
        ExpressionAttributeValues={':c': course_id}
    )
    return response.get('Items', [])

def get_submissions_by_student(student_id):
    response = submissions_table.scan(
        FilterExpression='student_id = :s',
        ExpressionAttributeValues={':s': student_id}
    )
    return response.get('Items', [])

def grade_submission(submission_id, grade, feedback, student_id):
    submissions_table.update_item(
        Key={'submission_id': submission_id},
        UpdateExpression='SET grade = :g, feedback = :f',
        ExpressionAttributeValues={':g': grade, ':f': feedback}
    )
    # Auto-notify student
    create_notification(student_id, f"Your project was graded: {grade}/100. Feedback: {feedback}")


# ─────────────────────────────────────────────
# NOTIFICATION OPERATIONS
# ─────────────────────────────────────────────
def create_notification(user_id, message):
    notif_id = str(uuid.uuid4())
    notifications_table.put_item(Item={
        'notif_id': notif_id,
        'user_id': user_id,
        'message': message,
        'read': False,
        'created_at': datetime.utcnow().isoformat()
    })

def get_notifications(user_id):
    response = notifications_table.scan(
        FilterExpression='user_id = :u',
        ExpressionAttributeValues={':u': user_id}
    )
    items = response.get('Items', [])
    return sorted(items, key=lambda x: x['created_at'], reverse=True)

def mark_notification_read(notif_id):
    notifications_table.update_item(
        Key={'notif_id': notif_id},
        UpdateExpression='SET #r = :t',
        ExpressionAttributeNames={'#r': 'read'},
        ExpressionAttributeValues={':t': True}
    )


# ─────────────────────────────────────────────
# QUIZ OPERATIONS
# ─────────────────────────────────────────────
def create_quiz(course_id, faculty_id, title, questions):
    """questions = [{'question': '...', 'options': [...], 'answer': '...'}]"""
    quiz_id = str(uuid.uuid4())
    quizzes_table.put_item(Item={
        'quiz_id': quiz_id,
        'course_id': course_id,
        'faculty_id': faculty_id,
        'title': title,
        'questions': questions,
        'created_at': datetime.utcnow().isoformat()
    })
    return quiz_id

def get_quizzes_by_course(course_id):
    response = quizzes_table.scan(
        FilterExpression='course_id = :c',
        ExpressionAttributeValues={':c': course_id}
    )
    return response.get('Items', [])

def get_quiz_by_id(quiz_id):
    response = quizzes_table.get_item(Key={'quiz_id': quiz_id})
    return response.get('Item')
