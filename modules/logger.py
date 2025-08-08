import mlflow
import os
import json
from datetime import datetime

def log_summary(model_name, article, summary_text):
    run_name = f"{model_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    with mlflow.start_run(run_name=run_name):
        mlflow.set_tag("model", model_name)
        mlflow.log_param("title", article['title'])
        mlflow.log_param("source", article['source']['name'])
        mlflow.log_param("url", article['url'])

        mlflow.log_metric("input_length", len(article['description'] or ""))
        mlflow.log_metric("summary_length", len(summary_text))

        filename = f"{model_name}_{datetime.now().strftime('%H%M%S')}.json"
        folder = f"mlflow_logs/summaries/{model_name.lower()}"
        os.makedirs(folder, exist_ok=True)

        path = os.path.join(folder, filename)
        with open(path, "w", encoding="utf-8") as f:
            json.dump({
                "title": article['title'],
                "source": article['source']['name'],
                "url": article['url'],
                "summary": summary_text
            }, f, indent=2)

        mlflow.log_artifact(path)
