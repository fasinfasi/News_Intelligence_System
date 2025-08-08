import torch
from transformers import PegasusTokenizer, PegasusForConditionalGeneration
from summarizer import Summarizer

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

