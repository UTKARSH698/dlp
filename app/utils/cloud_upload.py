import boto3
import os

def upload_to_s3(file_path, bucket_name, s3_key, aws_access_key, aws_secret_key):
    try:
        s3 = boto3.client('s3',
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key
        )
        s3.upload_file(file_path, bucket_name, s3_key)
        url = f"https://{bucket_name}.s3.amazonaws.com/{s3_key}"
        return url
    except Exception as e:
        return f"Upload failed: {e}"
