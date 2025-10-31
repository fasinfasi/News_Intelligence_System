import streamlit as st
import feedparser
import os
import sys
import pandas as pd
from datetime import datetime
import boto3
from botocore.exceptions import NoCredentialsError, ClientError

st.set_page_config(page_title="NewsBoss", page_icon="📰", layout="centered")

# Add modules path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'modules')))
from summarizers import pegasus_summarize, bert_summarize
from s3_storage import upload_summary_to_s3

S3_BUCKET_NAME = os.getenv("AWS_S3_BUCKET_NAME", "newsboss-storage")

# AWS S3 client
s3_client = boto3.client("s3")

# RSS Feed URL
RSS_FEED_URL = "https://feeds.bbci.co.uk/news/rss.xml"

# Fetch RSS articles
def fetch_rss_articles(feed_url):
    feed = feedparser.parse(feed_url)
    articles = []
    for entry in feed.entries:
        articles.append({
            "title": entry.title,
            "url": entry.link,
            "summary": entry.summary if "summary" in entry else ""
        })
    return articles

# Save feedback and upload to S3
def save_feedback(article_title, chosen_model, bert_summary, pegasus_summary):
    feedback_file = os.path.join("ab_testing", "feedbacks.csv")
    os.makedirs(os.path.dirname(feedback_file), exist_ok=True)

    feedback_data = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "article_title": article_title,
        "chosen_model": chosen_model,
        "bert_summary": bert_summary,
        "pegasus_summary": pegasus_summary
    }

    if os.path.exists(feedback_file):
        df = pd.read_csv(feedback_file)
        df = pd.concat([df, pd.DataFrame([feedback_data])], ignore_index=True)
    else:
        df = pd.DataFrame([feedback_data])

    # Save locally
    df.to_csv(feedback_file, index=False)

    # Try uploading to S3
    try:
        s3_client.upload_file(feedback_file, S3_BUCKET_NAME, "feedbacks.csv")
        return True, "✅ Feedback saved locally & uploaded to S3 as feedbacks.csv"
    except (NoCredentialsError, ClientError) as e:
        return False, f"⚠️ Feedback saved locally but S3 upload failed: {e}"

# ----------------- STREAMLIT APP -----------------
st.title("📰 NewsBoss - AI News Summarizer")

# Get latest articles
articles = fetch_rss_articles(RSS_FEED_URL)

# Dropdown for article selection
article_titles = [article["title"] for article in articles]
selected_title = st.selectbox("Choose a topic:", article_titles)

# Find the selected article object
selected_article = next((a for a in articles if a["title"] == selected_title), None)

if selected_article:
    st.write(f"**URL:** {selected_article['url']}")

    if st.button("Summarize with AI"):
        with st.spinner("Generating summaries... ⏳"):

            # Generate summaries
            pegasus_summary = pegasus_summarize(selected_article["summary"])
            bert_summary = bert_summarize(selected_article["summary"])

            # Side by side layout
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("🔹 BERT Extractive Summary")
                st.write(bert_summary)

            with col2:
                st.subheader("🔹 PEGASUS Abstractive Summary")
                st.write(pegasus_summary)

            # Upload to S3
            upload_summary_to_s3("PEGASUS", selected_article, pegasus_summary)
            upload_summary_to_s3("BERT", selected_article, bert_summary)

            st.success("✅ Summaries uploaded to S3 successfully!")

            # ---------------- Feedback section ----------------
            st.markdown("---")
            st.subheader("Which response do you prefer?")

            if "feedback_saved" not in st.session_state:
                choice = st.radio(
                    "Select the model you think gave a better summary:",
                    ("BERT", "PEGASUS"),
                    index=None,
                    key="feedback_choice"
                )

                if choice is not None:
                    ok, msg = save_feedback(
                        selected_article["title"], choice, bert_summary, pegasus_summary
                    )

                    if ok:
                        st.success(msg)
                    else:
                        st.error(msg)

                    # Mark feedback saved → hides options
                    st.session_state["feedback_saved"] = True
