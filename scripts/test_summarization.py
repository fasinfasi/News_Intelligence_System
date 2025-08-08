import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from modules.summarizers import pegasus_summarize, bert_summarize
from scripts.test_newsapi import fetch_news


if __name__ == "__main__":
    articles = fetch_news("AI and healthcare", page_size=1)

    if articles:
        article = articles[0]
        content = article['title'] + ". " + (article['description'] or "")

        print("\nOriginal Content:\n", content)

        print("\nPEGASUS Summary:")
        print(pegasus_summarize(content))

        print("\nBERT Summary:")
        print(bert_summarize(content))
