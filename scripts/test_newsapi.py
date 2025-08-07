import os
import requests
from dotenv import load_dotenv

# Load API key
load_dotenv()
API_KEY = os.getenv("NEWS_API_KEY")

def fetch_news(query="AI", language="en", page_size=5):
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": query,
        "language": language,
        "pageSize": page_size,
        "apiKey": API_KEY
    }
    response = requests.get(url, params=params)
    data = response.json()
    
    if response.status_code == 200:
        for i, article in enumerate(data['articles'], 1):
            print(f"\n{i}. {article['title']}\n   {article['description']}\n")
        return data['articles']
    else:
        print("Error:", data)
        return []

if __name__ == "__main__":
    fetch_news("Indian tariff")
