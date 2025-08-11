import os
from pyspark.sql import SparkSession
from scripts.test_newsapi import fetch_news

def fetch_news_articles():
    """
    Fetch news using NewsAPI and store as a Spark DataFrame.
    Output is saved as CSV in local storage for further processing.
    """
    topic = os.getenv("NEWS_TOPIC", "AI and healthcare")
    page_size = int(os.getenv("NEWS_PAGE_SIZE", 5))

    # Initialize Spark
    spark = SparkSession.builder \
        .appName("NewsBoss_Spark_Ingestion") \
        .getOrCreate()

    print(f"Fetching latest {page_size} articles about: {topic}")
    articles = fetch_news(topic, page_size=page_size)

    if not articles:
        print("No articles found.")
        return

    # Convert to DataFrame
    df = spark.createDataFrame(articles)

    # Save locally for next tasks
    output_path = "/opt/airflow/data/raw_news.csv"
    df.write.mode("overwrite").csv(output_path, header=True)

    print(f"Saved raw news to {output_path}")
    spark.stop()
