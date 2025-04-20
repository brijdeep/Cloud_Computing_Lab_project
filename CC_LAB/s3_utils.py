import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
import os
from dotenv import load_dotenv

# Load the environment variables from the .env file
load_dotenv()

# Get AWS credentials from environment variables
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_REGION = os.getenv('AWS_REGION')
S3_BUCKET_NAME = os.getenv('S3_BUCKET_NAME')

# Set up AWS S3 client
s3_client = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION
)

def upload_to_s3(file_path, s3_key):
    """
    Uploads a file to an S3 bucket
    :param file_path: Local file path to the file to upload
    :param s3_key: S3 object key (path) to store the file
    :return: None
    """
    try:
        # Open the file in binary mode and upload to S3
        with open(file_path, 'rb') as file:
            s3_client.upload_fileobj(file, S3_BUCKET_NAME, s3_key)
        print(f"File {file_path} uploaded to S3 with key {s3_key}")
    except FileNotFoundError:
        print(f"Error: The file {file_path} does not exist.")
    except NoCredentialsError:
        print("Error: AWS credentials are not provided.")
    except PartialCredentialsError:
        print("Error: Incomplete AWS credentials.")
    except Exception as e:
        print(f"Error: {e}")

def download_from_s3(s3_key, download_path):
    """
    Downloads a file from S3
    :param s3_key: S3 object key (path) of the file to download
    :param download_path: Local file path to store the downloaded file
    :return: None
    """
    try:
        # Download the file from S3 to the local file system
        with open(download_path, 'wb') as file:
            s3_client.download_fileobj(S3_BUCKET_NAME, s3_key, file)
        print(f"File downloaded from S3 with key {s3_key} to {download_path}")
    except NoCredentialsError:
        print("Error: AWS credentials are not provided.")
    except PartialCredentialsError:
        print("Error: Incomplete AWS credentials.")
    except Exception as e:
        print(f"Error: {e}")
