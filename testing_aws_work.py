import os
import boto3
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get AWS credentials & bucket
ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
REGION = os.getenv("AWS_REGION")
BUCKET_NAME = os.getenv("AWS_S3_BUCKET_NAME")

# Create S3 client
s3 = boto3.client(
    "s3",
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY,
    region_name=REGION
)

try:
    # Test file upload
    test_file_name = "test_upload.txt"
    with open(test_file_name, "w") as f:
        f.write("Hello from NewsBoss!")

    s3.upload_file(test_file_name, BUCKET_NAME, test_file_name)
    print(f"✅ File '{test_file_name}' uploaded successfully to bucket '{BUCKET_NAME}'.")
except Exception as e:
    print(f"❌ Error: {e}")
