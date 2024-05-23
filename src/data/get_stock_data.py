import finnhub
import os
import json
import src.enviorment_variables as env
from datetime import datetime

def main():
    finnhub_client = finnhub.Client(api_key=env.finnhub_api_key)

    # Get the stock prices for different companies and commodities
    btc_price = finnhub_client.quote('BTC-USD')  # Bitcoin price
    crude_oil_price = finnhub_client.quote('CL=F')  # Crude oil price
    gold_price = finnhub_client.quote('GC=F')  # Gold price
    eth_price = finnhub_client.quote('ETH-USD')  # Ethereum price
    msft_price = finnhub_client.quote('MSFT')  # Microsoft stock price # technology
    jpm_price = finnhub_client.quote('JPM')  # JPMorgan Chase stock price # finance
    jnj_price = finnhub_client.quote('JNJ')  # Johnson & Johnson stock price # healthcare
    xom_price = finnhub_client.quote('XOM')  # Exxon Mobil stock price # energy

    # Create the directory if it does not exist
    os.makedirs('data/preprocessed/finance', exist_ok=True)

    # Get the current timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    timestamp_filename = timestamp.replace(" ", "_").replace(":", "-")

    # Define the JSON file path
    json_file = f'data/preprocessed/finance/finance_data_{timestamp_filename}.json'

    # Create a dictionary to hold the stock prices
    stock_data = {
        'timestamp': timestamp,
        'BTC Price': btc_price['c'],
        'Crude Oil Price': crude_oil_price['c'],
        'Gold Price': gold_price['c'],
        'ETH Price': eth_price['c'],
        'MSFT Price': msft_price['c'],
        'JPM Price': jpm_price['c'],
        'JNJ Price': jnj_price['c'],
        'XOM Price': xom_price['c']
    }

    # Write the dictionary to a JSON file
    with open(json_file, 'w', encoding='utf-8') as file:
        json.dump(stock_data, file, ensure_ascii=False, indent=4)

    print(f"Data written to {json_file}")

if __name__ == "__main__":
    main()
