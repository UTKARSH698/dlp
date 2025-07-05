import boto3
import os

def upload_to_s3(file_path, s3_key):
    try:
        s3 = boto3.client(
            's3',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY'),
            aws_secret_access_key=os.getenv('AWS_SECRET_KEY')
        )

        bucket = os.getenv('AWS_BUCKET_NAME')
        s3.upload_file(file_path, bucket, s3_key)
        print(f"Uploaded {s3_key} to S3 bucket {bucket}")
        return True
    except Exception as e:
        print(f"[Upload Failed] {e}")
        return False


def generate_presigned_url(file_key, expires_in=3600):
    try:
        s3 = boto3.client(
            's3',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY'),
            aws_secret_access_key=os.getenv('AWS_SECRET_KEY')
        )
        url = s3.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': os.getenv('AWS_BUCKET_NAME'),
                'Key': file_key
            },
            ExpiresIn=expires_in
        )
        return url
    except Exception as e:
        print(f"[Presigned URL Error] {e}")
        return None
