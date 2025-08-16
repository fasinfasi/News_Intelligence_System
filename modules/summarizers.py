import torch
from transformers import PegasusTokenizer, PegasusForConditionalGeneration
from summarizer.bert import Summarizer
from s3_storage import upload_summary_to_s3  # <-- New import

# 1. PEGASUS summarizer (abstractive)
def pegasus_summarize(text, model_name="google/pegasus-xsum"):
    tokenizer = PegasusTokenizer.from_pretrained(model_name)
    model = PegasusForConditionalGeneration.from_pretrained(model_name)
    tokens = tokenizer(text, truncation=True, padding="longest", return_tensors="pt")
    summary_ids = model.generate(**tokens)
    return tokenizer.decode(summary_ids[0], skip_special_tokens=True)

# 2. BERT summarizer (extractive)
def bert_summarize(text):
    model = Summarizer()
    summary = model(text)
    return summary

if __name__ == "__main__":
    # Example article
    article = {
        "title": "AI Breakthrough in News Summarization",
        "url": "https://example.com/news/ai-breakthrough",
        "content": "Your long article text goes here..."
    }

    # Generate summaries
    pegasus_result = pegasus_summarize(article["content"])
    bert_result = bert_summarize(article["content"])

    # Upload to S3
    upload_summary_to_s3("PEGASUS", article, pegasus_result)
    upload_summary_to_s3("BERT", article, bert_result)
