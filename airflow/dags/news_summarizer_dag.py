from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators import PythonOperator
import sys

sys.path.append('/opt/airflow')
sys.path.append('/opt/airflow/dags')

from pipelines.spark_ingestion import fetch_news_articles
from pipelines.summarization import summarize_articles
from pipelines.logging_utils import log_to_s3_and_mlflow

default_args = {
    'owner': 'fasin',
    'depends_on_past': False,
    'email_on_failure': True,
    'email': 'fasinfasi17@gmail.com',
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    dag_id= 'news_summarizer_dag',
    default_args=default_args,
    description='Fetch news, summarize with PEGASUS & BERT, log to S3 & MLflow',
    schedule_interval=timedelta(hours=1),
    start_date=datetime(2025, 8, 10),
    catchup=False,
    tags=['news', 'nlp', 'summarization', 'mlops'],
) as dag:

    # --- Task 1: Fetch News with Spark ---
    fetch_task = PythonOperator(
        task_id='fetch_news',
        python_callable=fetch_news_articles
    )

    # --- Task 2: Summarize Articles ---
    summarize_task = PythonOperator(
        task_id='summarize_news',
        python_callable=summarize_articles
    )

    # --- Task 3: Log to S3 & MLflow ---
    log_task = PythonOperator(
        task_id='log_results',
        python_callable=log_to_s3_and_mlflow
    )

    # --- Task Order ---
    fetch_task >> summarize_task >> log_task
