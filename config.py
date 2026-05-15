class Config:
    # Set to True to use DynamoDB, False to use SQLite
    USE_AWS = False

    # AWS Configuration
    AWS_REGION = "ap-south-1"
    AWS_ACCESS_KEY = "YOUR_ACCESS_KEY"
    AWS_SECRET_KEY = "YOUR_SECRET_KEY"

    # SQLite Configuration
    SQLALCHEMY_DATABASE_URI = "sqlite:///cloud_ed.db"

    # DynamoDB Tables
    USERS_TABLE = "users"
    COURSES_TABLE = "courses"
    SUBMISSIONS_TABLE = "submissions"
    NOTIFICATIONS_TABLE = "notifications"
    QUIZZES_TABLE = "quizzes"