import requests
import csv
import os
from datetime import datetime
import json

import os

import src.helpers.latest_file as lf


    

import json
import csv
import os

def merge_and_save_data(article_data_file, finance_data_file, output_file):
    # Load the article data from JSON file
    with open(article_data_file, 'r', encoding='utf-8') as f:
        article_data = json.load(f)
    
    # Load the finance data from JSON file
    with open(finance_data_file, 'r', encoding='utf-8') as f:
        finance_data = json.load(f)
    
    # Merge the data
    
    merged_entry = {
        'date': finance_data['timestamp'],
        'BTC Price': finance_data['BTC Price'],
        'BTC High': finance_data['BTC High'],            # Highest price of Bitcoin during the trading day
        'BTC Low': finance_data['BTC Low'],             # Lowest price of Bitcoin during the trading day
        'BTC Open': finance_data['BTC Open'],            # Opening price of Bitcoin
        'BTC Previous Close': finance_data['BTC Previous Close'], # Previous closing price of Bitcoin
        'Crude Oil Price': finance_data['Crude Oil Price'],
        'Gold Price': finance_data['Gold Price'],
        'ETH Price': finance_data['ETH Price'],
        'MSFT Price': finance_data['MSFT Price'],
        'JPM Price': finance_data['JPM Price'],
        'JNJ Price': finance_data['JNJ Price'],
        'XOM Price': finance_data['XOM Price'],
        'Sentiment Article 1': article_data[0].get('predicted_class', 'null'),
        'Sentiment Article 2': article_data[1].get('predicted_class', 'null'),
        'Sentiment Article 3': article_data[2].get('predicted_class', 'null'),
    }
    
    # Define the columns for the CSV file
    columns = [
        'date', 'BTC Price', 'BTC High', 'BTC Low', 'BTC Open', 'BTC Previous Close',
        'Crude Oil Price', 'Gold Price', 'ETH Price', 'MSFT Price', 'JPM Price', 'JNJ Price', 'XOM Price',
        'Sentiment Article 1', 'Sentiment Article 2', 'Sentiment Article 3'
    ]
    
    # Define the output CSV file path
    
    # Check if the file exists
    file_exists = os.path.isfile(output_file)
    
    # Write the merged data to the CSV file
    with open(output_file, 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=columns)
        
        # Write the header row if the file is newly created
        if not file_exists:
            writer.writeheader()
        
        # Write the data row
        writer.writerow(merged_entry)
    
    print("Data saved to", output_file)


# Main function
def main():
    try:
        finance_dir = "data/preprocessed/finance/"
        article_dir = "data/preprocessed/articles/"
        output_file = "data/processed/finance_full_data.csv"

        latest_mbike_file, mbike_timestamp = lf.get_latest_file(finance_dir)
        latest_article_file, article_timestamp = lf.get_latest_file(article_dir)



        merge_and_save_data(latest_article_file, latest_mbike_file, output_file)
        

    except requests.RequestException as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()