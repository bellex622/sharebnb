import os
import logging
import boto3
from botocore.exceptions import ClientError
import requests

from dotenv import load_dotenv
load_dotenv()

aws_access_key_id = os.environ['AWS_ACCESS_KEY_ID']
aws_secret_access_key = os.environ['AWS_SECRET_ACCESS_KEY']
OBJECT_NAME_TO_UPLOAD = 'cat.jpg'


def create_presigned_post(bucket_name='sharebnb-r32', object_name=OBJECT_NAME_TO_UPLOAD,
                          fields=None, conditions=None, expiration=3600):
    """Generate a presigned URL S3 POST request to upload a file

    :param bucket_name: string
    :param object_name: string
    :param fields: Dictionary of prefilled form fields
    :param conditions: List of conditions to include in the policy
    :param expiration: Time in seconds for the presigned URL to remain valid
    :return: Dictionary with the following keys:
        url: URL to post to
        fields: Dictionary of form fields and values to submit with the POST
    :return: None if error.
    """

    # Generate a presigned S3 POST URL
    s3_client = boto3.client('s3', aws_access_key_id=aws_access_key_id,
                             aws_secret_access_key=aws_secret_access_key)
    try:
        response = s3_client.generate_presigned_post(bucket_name,
                                                     object_name,
                                                     fields, conditions, expiration)
    except ClientError as e:
        logging.error(e)
        return None

    # The response contains the presigned URL and required fields
    return response


response = create_presigned_post()
print(response)



files = { 'file': open(OBJECT_NAME_TO_UPLOAD, 'rb')}
r = requests.post(response['url'], data=response['fields'], files=files)
print(r.status_code)

