import torch
from transformers import PegasusTokenizer, PegasusForConditionalGeneration
from summarizer.bert import Summarizer
from s3_storage import upload_summary_to_s3

PEGASUS_MODEL_NAME = "google/pegasus-xsum"

pegasus_tokenizer = PegasusTokenizer.from_pretrained(PEGASUS_MODEL_NAME)
pegasus_model = PegasusForConditionalGeneration.from_pretrained(PEGASUS_MODEL_NAME)

bert_model = Summarizer()

# 1. PEGASUS Summarizer (abstractive)
def pegasus_summarize(text):
    tokens = pegasus_tokenizer(
        text,
        truncation=True,
        padding="longest",
        return_tensors="pt"
    )
    summary_ids = pegasus_model.generate(
        **tokens,
        min_length=60,   # about 3–4 lines
        max_length=140,  # about 5–6 lines
        do_sample=False
    )
    return pegasus_tokenizer.decode(summary_ids[0], skip_special_tokens=True)

# BERT Summarizer (extractive)
def bert_summarize(text):
    summary = bert_model(text, num_sentences=8)  # ~4 sentences
    return summary

if __name__ == "__main__":
    article = {
        "title": "AI Breakthrough in News Summarization",
        "url": "https://example.com/news/ai-breakthrough",
        "content": "Your long article text goes here..."
    }

    pegasus_result = pegasus_summarize(article["content"])
    bert_result = bert_summarize(article["content"])

    # Print locally
    print("\n🔹 PEGASUS Summary:\n", pegasus_result)
    print("\n🔹 BERT Summary:\n", bert_result)

    # Upload to S3 (if needed)
    upload_summary_to_s3("PEGASUS", article, pegasus_result)
    upload_summary_to_s3("BERT", article, bert_result)
