import streamlit as st
import feedparser
import os
import sys
import json
from datetime import datetime

st.set_page_config(page_title="NewsBoss", page_icon="📰", layout="centered")

# Add modules path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'modules')))
from summarizers import pegasus_summarize, bert_summarize
from s3_storage import upload_summary_to_s3, upload_feedback_to_s3

# RSS Feed URL
RSS_FEED_URL = "https://feeds.bbci.co.uk/news/rss.xml"


# ---------------- Fetch RSS articles ----------------
def fetch_rss_articles(feed_url):
    """Fetch articles from RSS feed."""
    feed = feedparser.parse(feed_url)
    articles = []
    for entry in feed.entries:
        articles.append({
            "title": entry.title,
            "url": entry.link,
            "summary": entry.summary if "summary" in entry else ""
        })
    return articles


# ---------------- Save feedback locally AND to S3 ----------------
def save_feedback(article_title, chosen_model, bert_summary, pegasus_summary):
    """
    Save feedback both locally as JSON and to S3.
    Returns (success: bool, message: str).
    """
    # Define feedback file path
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    feedback_dir = os.path.join(project_root, 'ab_testing', 'feedbacks')
    os.makedirs(feedback_dir, exist_ok=True)
    feedback_file = os.path.join(feedback_dir, 'feedbacks.json')

    # Prepare feedback data
    feedback_data = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "article_title": article_title,
        "chosen_model": chosen_model,
        "bert_summary": bert_summary,
        "pegasus_summary": pegasus_summary
    }

    local_success = False
    s3_success = False
    messages = []

    # -------- Save locally --------
    try:
        # Load existing feedback data
        data = []
        if os.path.exists(feedback_file):
            try:
                with open(feedback_file, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if content:
                        loaded = json.loads(content)
                        if isinstance(loaded, list):
                            data = loaded
                        else:
                            # Backup invalid format and start fresh
                            backup_file = feedback_file + '.bak'
                            if os.path.exists(backup_file):
                                os.remove(backup_file)
                            os.rename(feedback_file, backup_file)
                            data = []
            except (json.JSONDecodeError, Exception):
                # Backup corrupted file and start fresh
                try:
                    backup_file = feedback_file + '.bak'
                    if os.path.exists(backup_file):
                        os.remove(backup_file)
                    os.rename(feedback_file, backup_file)
                except Exception:
                    pass
                data = []

        # Append new feedback
        data.append(feedback_data)

        # Write atomically using temporary file
        tmp_file = feedback_file + '.tmp'
        with open(tmp_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        # Atomic replace
        if os.path.exists(feedback_file):
            os.remove(feedback_file)
        os.rename(tmp_file, feedback_file)

        local_success = True
        messages.append(f"✅ Thank you for your Feedback which is really useful to us☺️")

    except Exception as e:
        messages.append(f"⚠️ Failed to save feedback locally: {str(e)}")

    # -------- Upload to S3 --------
    try:
        s3_success, s3_error = upload_feedback_to_s3(feedback_data)
        
        if s3_success:
            messages.append("✅ Feedback uploaded to S3 successfully!")
        else:
            messages.append(f"⚠️ Failed to upload feedback to S3: {s3_error}")
    
    except Exception as e:
        messages.append(f"⚠️ S3 upload error: {str(e)}")

    # Determine overall success
    overall_success = local_success or s3_success
    combined_message = "\n\n".join(messages)
    
    return overall_success, combined_message


# ---------------- STREAMLIT APP ----------------
st.title("📰 NewsBoss - AI News Summarizer")

# Fetch latest articles
articles = fetch_rss_articles(RSS_FEED_URL)

# Article selection dropdown
article_titles = [article["title"] for article in articles]

# Preserve previous selection across reruns
prev_selected = st.session_state.get("selected_title", None)
if prev_selected and prev_selected not in article_titles:
    article_titles.insert(0, prev_selected)

# Use session_state key for persistence
selected_title = st.selectbox("Choose a headline from these latest news:", article_titles, key="selected_title")

# Map titles to articles for lookup
title_to_article = {a["title"]: a for a in articles}
selected_article = title_to_article.get(selected_title)

if selected_article:
    st.write(f"**URL:** {selected_article['url']}")

    if st.button("Summarize with AI"):
        with st.spinner("Generating summaries... ⏳"):

            # Generate summaries
            pegasus_summary = pegasus_summarize(selected_article["summary"])
            bert_summary = bert_summarize(selected_article["summary"])

            # Store summaries in session state for feedback
            st.session_state["bert_summary"] = bert_summary
            st.session_state["pegasus_summary"] = pegasus_summary
            st.session_state["current_article"] = selected_article

            # Display summaries side by side
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("🔹 BERT Extractive Summary")
                st.write(bert_summary)

            with col2:
                st.subheader("🔹 PEGASUS Abstractive Summary")
                st.write(pegasus_summary)

            # Upload summaries to S3
            upload_summary_to_s3("PEGASUS", selected_article, pegasus_summary)
            upload_summary_to_s3("BERT", selected_article, bert_summary)

            st.success("✅ Summaries uploaded to S3 successfully!")

            # Reset feedback saved state for new summary
            if "feedback_saved" in st.session_state:
                del st.session_state["feedback_saved"]
            if "feedback_message" in st.session_state:
                del st.session_state["feedback_message"]

    # ---------------- Feedback Section ----------------
    # Show feedback section only if summaries exist in session state
    if "bert_summary" in st.session_state and "pegasus_summary" in st.session_state:
        st.markdown("---")
        st.subheader("Which response do you prefer?")

        # Check if feedback already saved for current article
        if st.session_state.get("feedback_saved", False):
            # Display the saved feedback message
            feedback_msg = st.session_state.get("feedback_message", "✅ Thank you for your feedback!")
            
            # Check if there were any warnings in the message
            if "⚠️" in feedback_msg:
                st.warning(feedback_msg)
            else:
                st.success(feedback_msg)
        else:
            # Create two columns for feedback buttons
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("👍 Prefer BERT", use_container_width=True, key="feedback_bert"):
                    # Set the flag IMMEDIATELY before any processing
                    st.session_state["feedback_saved"] = True
                    
                    with st.spinner("Saving feedback..."):
                        success, message = save_feedback(
                            st.session_state["current_article"]["title"],
                            "BERT",
                            st.session_state["bert_summary"],
                            st.session_state["pegasus_summary"]
                        )
                        
                        st.session_state["feedback_message"] = message
                    
                    # Force rerun to show the success message
                    st.rerun()
            
            with col2:
                if st.button("👍 Prefer PEGASUS", use_container_width=True, key="feedback_pegasus"):
                    # Set the flag IMMEDIATELY before any processing
                    st.session_state["feedback_saved"] = True
                    
                    with st.spinner("Saving feedback..."):
                        success, message = save_feedback(
                            st.session_state["current_article"]["title"],
                            "PEGASUS",
                            st.session_state["bert_summary"],
                            st.session_state["pegasus_summary"]
                        )
                        
                        st.session_state["feedback_message"] = message
                    
                    # Force rerun to show the success message
                    st.rerun()