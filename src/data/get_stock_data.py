import finnhub
import os
import json
import src.enviorment_variables as env
from datetime import datetime
import time

def get_price(client, symbol):
    retry_count = 0
    max_retries = 3
    while retry_count < max_retries:
        price = client.quote(symbol)
        print(price)
        if price['c'] != 0:  # Check if the price is not zero
            return price
        else:
            print("retlying...")
            retry_count += 1
            time.sleep(5)  # Wait for 5 seconds before retrying
    return None  # Return None if max retries reached

def main():
    finnhub_client = finnhub.Client(api_key=env.finnhub_api_key)

    btc_price = get_price(finnhub_client, 'BTC-USD')  # Get the price of Bitcoin
    crude_oil_price = get_price(finnhub_client, 'CL=F')  # Get the price of Crude Oil
    gold_price = get_price(finnhub_client, 'GC=F')  # Get the price of Gold
    eth_price = get_price(finnhub_client, 'ETH-USD')  # Get the price of Ethereum
    msft_price = get_price(finnhub_client, 'MSFT')  # Get the price of Microsoft (technology)
    jpm_price = get_price(finnhub_client, 'JPM')  # Get the price of JPMorgan Chase (finance)
    jnj_price = get_price(finnhub_client, 'JNJ')  # Get the price of Johnson & Johnson (healthcare)
    xom_price = get_price(finnhub_client, 'XOM')  # Get the price of Exxon Mobil (energy)

    # Check if any price is still None
    if any(price is None for price in [btc_price, crude_oil_price, gold_price, eth_price, msft_price, jpm_price, jnj_price, xom_price]):
        print("Failed to fetch prices for one or more symbols. Please check your API key or try again later.")
        return

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
