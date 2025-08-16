import boto3
import os
from datetime import datetime

# Load environment variables
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_BUCKET_NAME = os.getenv("AWS_S3_BUCKET_NAME", "newsboss-storage")
AWS_REGION = os.getenv("AWS_REGION", "ap-south-1")

# Create S3 client
s3_client = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
    region_name=AWS_REGION
)

def upload_summary_to_s3(model_type, article, summary_text):
    """
    Uploads a news summary to S3 with a meaningful filename.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_title = "".join(c for c in article["title"] if c.isalnum() or c in (" ", "_")).strip().replace(" ", "_")

    file_name = f"{model_type}_{safe_title}_{timestamp}.txt"

    # File content
    file_content = (
        f"Title: {article['title']}\n"
        f"URL: {article['url']}\n"
        f"Model: {model_type}\n"
        f"Summary:\n{summary_text}\n"
    )

    try:
        s3_client.put_object(
            Bucket=AWS_BUCKET_NAME,
            Key=file_name,
            Body=file_content.encode("utf-8")
        )
        print(f"✅ Summary uploaded to S3: {file_name}")
    except Exception as e:
        print(f"❌ Error uploading summary to S3: {e}")
