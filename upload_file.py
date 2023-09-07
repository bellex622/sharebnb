import os
import boto3
from dotenv import load_dotenv
load_dotenv()

aws_access_key_id = os.environ['AWS_ACCESS_KEY_ID']
aws_secret_access_key = os.environ['AWS_SECRET_ACCESS_KEY']
OBJECT_NAME_TO_UPLOAD = 'cat.jpg'
bucket = os.environ['BUCKET']

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def upload_file():
    s3 = boto3.client(
        's3',
        "us-east-1",
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
)
    s3.upload_file('cat.jpg', bucket, 'cat2.jpg', {'ContentType': 'image/jpeg'})


