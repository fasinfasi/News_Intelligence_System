# 📰 NewsBoss - AI-Powered News Intelligence System

<div align="center">

![Python](https://img.shields.io/badge/Python-3.12-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-Latest-red.svg)
![PyTorch](https://img.shields.io/badge/PyTorch-Latest-orange.svg)
![AWS](https://img.shields.io/badge/AWS-S3-orange.svg)

**An intelligent news aggregation and summarization platform powered by advanced AI models**

[Features](#-features) • [Installation](#-installation) • [Usage](#-usage) • [Configuration](#-configuration) • [Project Structure](#-project-structure)

</div>

---

## 🎯 Overview

NewsBoss is a fully automated platform that aggregates news articles from multiple public sources, generates intelligent summaries using state-of-the-art AI models (BERT and PEGASUS), and provides an interactive dashboard for users to compare and evaluate different summarization approaches. The system includes A/B testing capabilities for model comparison and stores all summaries and feedback in AWS S3 for scalability and analysis.

**Use Cases:**
- 📊 Financial intelligence and market monitoring
- 🏛️ Political risk analysis
- 📈 Marketing intelligence and trend tracking
- 🚨 Crisis response and news monitoring
- 📰 Personalized news consumption

---

## ✨ Features

### 🤖 Dual-Model Summarization
- **BERT Extractive Summarization**: Preserves original sentences, maintaining factual accuracy
- **PEGASUS Abstractive Summarization**: Generates concise, human-like summaries
- Side-by-side comparison for easy evaluation

### 📡 News Aggregation
- Real-time RSS feed parsing from multiple sources
- Automatic article fetching and processing
- Support for custom RSS feed URLs

### 💾 Cloud Storage Integration
- Automatic upload of summaries to AWS S3
- Organized storage with meaningful filenames
- Persistent feedback storage for A/B testing

### 🔬 A/B Testing Framework
- User feedback collection (BERT vs PEGASUS preference)
- Local and cloud-based feedback storage
- Data-driven model comparison and evaluation

### 🎨 Interactive Dashboard
- Clean, modern Streamlit-based UI
- Real-time article selection and summarization
- Intuitive feedback mechanism

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| **Frontend** | Streamlit |
| **AI Models** | Transformers (Hugging Face), BERT, PEGASUS |
| **Deep Learning** | PyTorch |
| **NLP** | spaCy, SentencePiece |
| **Cloud Storage** | AWS S3 (boto3) |
| **Data Sources** | RSS Feeds (feedparser) |
| **Environment** | Python 3.12+ |

---

## 📦 Installation

### Prerequisites

- Python 3.12 or higher
- AWS Account (for S3 storage)
- pip package manager

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/News_Summarizer_System.git
cd News_Summarizer_System
```

### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

**Note:** The first run will download the PEGASUS and BERT models (~1.5GB), which may take a few minutes.

### Step 4: Configure AWS Credentials

Create a `.env` file in the project root:

```env
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here
AWS_S3_BUCKET_NAME=your-bucket-name
AWS_REGION=ap-south-1
```

**Security Note:** Never commit your `.env` file. It's already in `.gitignore`.

---

## 🚀 Usage

### Starting the Application

```bash
# Make sure you're in the project root directory
streamlit run frontend/app.py
```

The application will open in your default browser at `http://localhost:8501`

### Using the Dashboard

1. **Select an Article**: Choose from the latest news headlines in the dropdown
2. **Generate Summaries**: Click "Summarize with AI" to generate both BERT and PEGASUS summaries
3. **Compare Results**: View side-by-side summaries to evaluate both approaches
4. **Provide Feedback**: Select which model you prefer (BERT or PEGASUS) to contribute to A/B testing

### Programmatic Usage

You can also use the summarization modules directly in your Python code:

```python
from modules.summarizers import bert_summarize, pegasus_summarize

# Example article text
article_text = "Your long article text goes here..."

# Generate summaries
bert_summary = bert_summarize(article_text)
pegasus_summary = pegasus_summarize(article_text)

print("BERT Summary:", bert_summary)
print("PEGASUS Summary:", pegasus_summary)
```

---

## ⚙️ Configuration

### AWS S3 Setup

1. **Create an S3 Bucket**: 
   - Log in to AWS Console
   - Create a new S3 bucket (e.g., `newsboss-storage`)
   - Note your region (default: `ap-south-1`)

2. **Create IAM User**:
   - Go to IAM → Users → Create User
   - Attach policy: `AmazonS3FullAccess` (or create custom policy with PutObject, GetObject permissions)
   - Generate Access Key and Secret Key
   - Add credentials to `.env` file

3. **Update `.env` File**:
   ```env
   AWS_S3_BUCKET_NAME=your-bucket-name
   AWS_REGION=your-region
   ```

### RSS Feed Configuration

To change the news source, modify `RSS_FEED_URL` in `frontend/app.py`:

```python
RSS_FEED_URL = "https://feeds.bbci.co.uk/news/rss.xml"  # Change to your preferred RSS feed
```

**Popular RSS Feed Sources:**
- BBC News: `https://feeds.bbci.co.uk/news/rss.xml`
- Reuters: `https://www.reutersagency.com/feed/?best-topics=business-finance&post_type=best`
- CNN: `http://rss.cnn.com/rss/edition.rss`

---

## 📁 Project Structure

```
News_Summarizer_System/
│
├── frontend/
│   └── app.py                 # Streamlit web application
│
├── modules/
│   ├── __init__.py
│   ├── summarizers.py         # BERT and PEGASUS summarization models
│   └── s3_storage.py          # AWS S3 upload functionality
│
├── ab_testing/
│   └── feedbacks/
│       └── feedbacks.json     # Local feedback storage (backup)
│
├── venv/                      # Virtual environment (ignored)
│
├── requirements.txt           # Python dependencies
├── .env                       # Environment variables (ignored)
├── .gitignore                 # Git ignore rules
└── README.md                  # This file
```

---

## 📋 Dependencies

| Package | Purpose |
|---------|---------|
| `streamlit` | Web application framework |
| `transformers` | Hugging Face transformers library |
| `torch` | PyTorch deep learning framework |
| `bert-extractive-summarizer` | BERT-based extractive summarization |
| `spacy` | Natural language processing |
| `sentencepiece` | Tokenization for PEGASUS |
| `boto3` | AWS SDK for Python |
| `feedparser` | RSS feed parsing |
| `python-dotenv` | Environment variable management |
| `requests` | HTTP library |

---

## 🔬 A/B Testing

The system includes a built-in A/B testing framework to compare BERT and PEGASUS models:

- **Feedback Collection**: Users can select their preferred summary model
- **Data Storage**: Feedback is stored both locally (`ab_testing/feedbacks/feedbacks.json`) and in S3
- **Analysis Ready**: JSON format allows easy analysis of model preferences
- **Metadata**: Each feedback entry includes timestamp, article title, and both summaries

### Feedback Data Structure

```json
{
  "timestamp": "2024-01-15 14:30:00",
  "article_title": "Example News Article",
  "chosen_model": "BERT",
  "bert_summary": "Summary text...",
  "pegasus_summary": "Summary text..."
}
```

---


## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request🫱🏼‍🫲🏼

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 🙏 Acknowledgments

- **Hugging Face** for the transformers library and pre-trained models
- **Streamlit** for the amazing web framework
- **AWS** for cloud storage infrastructure
- **BBC News** for providing RSS feed access

---

## Contributor
**Fasin**👨🏻‍💻 

*Follow for more🚶🏻‍➡️*
