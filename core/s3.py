from core.aws import load_config
import boto3

def read_object_from_s3(bucket, key, region_name='eu-central-1'):
    config = load_config()
    session = boto3.Session(
        aws_access_key_id=config['aws_access_key_id'],
        aws_secret_access_key=config['aws_secret_access_key'],
    )
    s3 = session.resource('s3', region_name=region_name)
    bucket = s3.Bucket(bucket)
    s3object = bucket.Object(key)
    response = s3object.get()
    bytes = response['Body'].read()
    return bytes


def write_object_to_s3(file_bytes, bucket, key, region_name='eu-central-1'):
    config = load_config()
    session = boto3.Session(
        aws_access_key_id=config['aws_access_key_id'],
        aws_secret_access_key=config['aws_secret_access_key'],
    )
    s3 = session.resource('s3', region_name)
    bucket = s3.Bucket(bucket)
    s3object = bucket.Object(key)
    s3object.put(Body=file_bytes)


def delete_object_on_s3(bucket, key, region_name='eu-central-1'):
    config = load_config()
    session = boto3.Session(
        aws_access_key_id=config['aws_access_key_id'],
        aws_secret_access_key=config['aws_secret_access_key'],
    )
    s3 = session.resource('s3', region_name)
    bucket = s3.Bucket(bucket)
    s3object = bucket.Object(key)
    s3object.delete()
