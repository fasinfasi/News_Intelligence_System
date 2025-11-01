import boto3
import os
import re
import hashlib
import json
import io
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
    # Create Keep it readable while removing punctuation and limiting length.
    raw_title = (article.get("title") or "").strip()
    # fallback to URL when title missing
    if not raw_title:
        raw_title = article.get("url", "")

    # Remove punctuation except word chars and spaces, then replace whitespace/hyphens with underscore
    slug = re.sub(r"[^\w\s-]", "", raw_title)
    slug = re.sub(r"[\s-]+", "_", slug).strip("_")
    slug = slug[:100]  # limit length to avoid very long filenames

    # short deterministic hash suffix from the raw title
    hash_suffix = hashlib.sha1(raw_title.encode("utf-8")).hexdigest()[:8]

    safe_title = f"{slug}_{hash_suffix}" if slug else hash_suffix

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


def upload_feedback_to_s3(feedback_data):
    """
    Appends feedback data to the feedbacks.json file in S3.
    Downloads existing JSON, appends new entry, and uploads back.
    """
    s3_key = 'ab_testing/feedbacks/feedbacks.json'
    
    try:
        # Try to download existing JSON from S3
        try:
            response = s3_client.get_object(Bucket=AWS_BUCKET_NAME, Key=s3_key)
            existing_json = response['Body'].read().decode('utf-8')
            data = json.loads(existing_json)
            if not isinstance(data, list):
                data = []
        except s3_client.exceptions.NoSuchKey:
            # File doesn't exist yet, create empty list
            data = []
        except json.JSONDecodeError:
            # Corrupted JSON, start fresh
            data = []
        except Exception:
            # Any other error, create empty list
            data = []
        
        # Append new feedback
        data.append(feedback_data)
        
        # Convert to JSON string with proper formatting
        json_content = json.dumps(data, ensure_ascii=False, indent=2)
        
        # Upload back to S3
        s3_client.put_object(
            Bucket=AWS_BUCKET_NAME,
            Key=s3_key,
            Body=json_content.encode('utf-8'),
            ContentType='application/json',
            Metadata={
                'uploaded_by': 'newsboss_frontend',
                'last_updated': feedback_data['timestamp']
            }
        )
        
        print(f"✅ Feedback uploaded to S3: {s3_key}")
        return True, None
    except Exception as e:
        error_msg = f"Error uploading feedback to S3: {str(e)}"
        print(f"❌ {error_msg}")
        return False, error_msg