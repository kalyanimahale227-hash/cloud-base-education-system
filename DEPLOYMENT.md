# EC2 Deployment Guide for CloudClass

Follow these steps to deploy the CloudClass Education System on an AWS EC2 instance.

## 1. Launch EC2 Instance
- **AMI**: Ubuntu 22.04 LTS
- **Instance Type**: t2.micro (Free Tier)
- **Security Group**: Allow TCP Port 80 (HTTP) and Port 22 (SSH).

## 2. Server Setup
Connect to your instance via SSH:
```bash
ssh -i "your-key.pem" ubuntu@your-ec2-ip
```

Update system and install dependencies:
```bash
sudo apt update
sudo apt install python3-pip python3-venv git -y
```

## 3. Clone and Initialize Project
```bash
git clone <your-repo-url>
cd cloud_ed_system
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 4. Configure Environment
```bash
cp .env.example .env
nano .env
# Enter your AWS Access Keys and set USE_AWS=True
```

## 5. Initialize DynamoDB
```bash
python3 setup_tables.py
```

## 6. Run with Gunicorn
Install Gunicorn:
```bash
pip install gunicorn
```

Run the application:
```bash
gunicorn --bind 0.0.0.0:80 app:app
```

## 7. AWS IAM Permissions
Ensure your EC2 instance (or the Access Keys provided) has the `AmazonDynamoDBFullAccess` policy attached to interact with the database.
