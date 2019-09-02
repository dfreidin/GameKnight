import boto3
import base64
from botocore.exceptions import ClientError
from os import getenv
import json


def get_secret():
    secret_name = getenv("DB_SECRET", "db/djf-dev")
    region_name = getenv("AWS_REGION", "us-west-2")
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )
    get_secret_value_response = client.get_secret_value(
        SecretId=secret_name
    )
    secret = get_secret_value_response.get('SecretString')
    return json.loads(secret)