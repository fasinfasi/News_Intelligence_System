import sys
import os
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from modules.summarizers import pegasus_summarize, bert_summarize
from scripts.test_newsapi import fetch_news
from modules.logger import log_summary

def summarize_articles():
    articles = fetch_news("AI and healthcare", page_size=1)
    results = []

    if articles:
        for article in articles:
            content = article['title'] + ". " + (article['description'] or "")
            pegasus_summary = pegasus_summarize(content)
            bert_summary = bert_summarize(content)

            results.append({
                "title": article['title'],
                "pegasus_summary": pegasus_summary,
                "bert_summary": bert_summary
            })

            log_summary("PEGASUS", article, pegasus_summary)
            log_summary("BERT", article, bert_summary)

    # Save for logging_utils.py
    os.makedirs("/opt/airflow/data", exist_ok=True)
    with open("/opt/airflow/data/final_summaries.json", "w") as f:
        json.dump(results, f, indent=2)

    print("Summaries saved for logging.")
