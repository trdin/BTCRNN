import os
import json
import yfinance as yf
import requests
from datetime import datetime
from bs4 import BeautifulSoup

def main():
    btc_info = yf.Ticker("BTC")
    news = btc_info.news

    # Extract top 3 articles
    top_articles = news[:3]

    articles_data = []

    for article in top_articles:
        title = article['title']
        link = article['link']
        print(f"Title: {title}\nLink: {link}\n")
        headers = {
            'accept': '*/*',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'en-US,en;q=0.9',
            'referer': 'https://www.google.com',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36 Edg/85.0.564.44'
        }

        # Send the GET request
        response = requests.get(link, headers=headers)

        if response.status_code == 200:
            # Parse the HTML content
            soup = BeautifulSoup(response.content, 'html.parser')

            # Attempt to extract the main content of the article
            paragraphs = soup.find_all('p')
            article_text = "\n".join([p.get_text() for p in paragraphs])

            # Print the article text
            print(f"Content:\n{article_text}\n")

            # Add the article data to the list
            articles_data.append({
                'title': title,
                'link': link,
                'content': article_text
            })
        else:
            print(f"Failed to fetch the article content from {link}")

    # Create the directory if it doesn't exist
    os.makedirs('data/raw', exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    timestamp_filename = timestamp.replace(" ", "_").replace(":", "-")


    # Write the articles data to a JSON file
    with open('data/raw/articles_data_'+timestamp_filename+'.json', 'w', encoding='utf-8') as f:
        json.dump(articles_data, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()
