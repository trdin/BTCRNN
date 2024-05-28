
import yfinance as yf
import requests
import sys


def check_yahoo_finance_api():
    try:
        btc_info = yf.Ticker("BTC-USD")
        news = btc_info.news
        return news is not None
    except Exception as e:
        print(f"Error checking Yahoo Finance API: {e}")
        return False

def check_news_article_fetching(news):
    if not news:
        print("No news articles found.")
        return False

    headers = {
        'accept': '*/*',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9',
        'referer': 'https://www.google.com',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36 Edg/85.0.564.44'
    }

    article = news[0]
    link = article['link']

    try:
        response = requests.get(link, headers=headers)
        return response.status_code == 200
    except requests.RequestException as e:
        print(f"Error fetching news article: {e}")
        return False



def health_check():
    
    print("Checking Yahoo Finance API...")
    if not check_yahoo_finance_api():
        print("Yahoo Finance API check failed.")
        sys.exit(1)
        return

    btc_info = yf.Ticker("BTC-USD")
    news = btc_info.news

    print("Checking news article fetching...")
    if not check_news_article_fetching(news):
        print("News article fetching check failed.")
        sys.exit(1)
        return

    print("All health checks passed.")

if __name__ == "__main__":
    health_check()


def main():
    health_check()