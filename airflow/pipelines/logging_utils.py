import os
import json
import mlflow
import boto3
from datetime import datetime

def log_to_s3_and_mlflow():
    """
    Upload final summaries to AWS S3 and log metadata/metrics to MLflow.
    """
    s3_bucket = os.getenv("AWS_S3_BUCKET")
    s3_key_prefix = os.getenv("S3_KEY_PREFIX", "newsboss/results")

    # Load summarized file
    summary_file = "/opt/airflow/data/final_summaries.json"
    if not os.path.exists(summary_file):
        print("No summary file found.")
        return

    # --- Upload to S3 ---
    s3_client = boto3.client(
        's3',
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
    )

    file_key = f"{s3_key_prefix}/summaries_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    s3_client.upload_file(summary_file, s3_bucket, file_key)

    print(f"Uploaded summaries to s3://{s3_bucket}/{file_key}")

    # --- Log to MLflow ---
    mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI", "http://mlflow:5000"))
    mlflow.set_experiment("NewsBoss_Summaries")

    with mlflow.start_run():
        mlflow.log_param("source", "NewsAPI")
        mlflow.log_param("model_pegasus", "google/pegasus-xsum")
        mlflow.log_param("model_bert", "bert-extractive-summarizer")
        mlflow.log_artifact(summary_file)

        with open(summary_file, "r") as f:
            summaries = json.load(f)
        mlflow.log_metric("num_summaries", len(summaries))

    print("Logged summaries to MLflow")
