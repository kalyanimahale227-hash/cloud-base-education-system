import boto3
import time
from config import Config

def create_tables():
    dynamodb = boto3.resource(
        'dynamodb',
        region_name=Config.AWS_REGION,
        aws_access_key_id=Config.AWS_ACCESS_KEY,
        aws_secret_access_key=Config.AWS_SECRET_KEY
    )

    tables = [
        {
            'TableName': Config.USERS_TABLE,
            'KeySchema': [{'AttributeName': 'user_id', 'KeyType': 'HASH'}],
            'AttributeDefinitions': [{'AttributeName': 'user_id', 'AttributeType': 'S'}],
            'ProvisionedThroughput': {'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
        },
        {
            'TableName': Config.COURSES_TABLE,
            'KeySchema': [{'AttributeName': 'course_id', 'KeyType': 'HASH'}],
            'AttributeDefinitions': [{'AttributeName': 'course_id', 'AttributeType': 'S'}],
            'ProvisionedThroughput': {'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
        },
        {
            'TableName': Config.SUBMISSIONS_TABLE,
            'KeySchema': [{'AttributeName': 'submission_id', 'KeyType': 'HASH'}],
            'AttributeDefinitions': [{'AttributeName': 'submission_id', 'AttributeType': 'S'}],
            'ProvisionedThroughput': {'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
        },
        {
            'TableName': Config.NOTIFICATIONS_TABLE,
            'KeySchema': [{'AttributeName': 'notif_id', 'KeyType': 'HASH'}],
            'AttributeDefinitions': [{'AttributeName': 'notif_id', 'AttributeType': 'S'}],
            'ProvisionedThroughput': {'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
        },
        {
            'TableName': Config.QUIZZES_TABLE,
            'KeySchema': [{'AttributeName': 'quiz_id', 'KeyType': 'HASH'}],
            'AttributeDefinitions': [{'AttributeName': 'quiz_id', 'AttributeType': 'S'}],
            'ProvisionedThroughput': {'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
        }
    ]

    for table_info in tables:
        try:
            print(f"Creating table {table_info['TableName']}...")
            table = dynamodb.create_table(**table_info)
            print(f"Table {table_info['TableName']} creation initiated.")
        except Exception as e:
            print(f"Error creating {table_info['TableName']}: {e}")

    print("\nWaiting for tables to be created...")
    time.sleep(5)
    print("Setup process finished. Please check your AWS Console.")

if __name__ == "__main__":
    create_tables()
