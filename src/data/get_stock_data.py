import finnhub
import os
import json
import src.enviorment_variables as env
from datetime import datetime, timezone
import time
import sys
import requests
import yfinance as yf



def btcOtherDataFailSafe(symbol, current_price):
    try:
        btc = yf.Ticker(symbol)
        btc_info = btc.info

        result = {
            'c': current_price,
            'h': btc_info.get('regularMarketDayHigh', ''),
            'l': btc_info.get('regularMarketDayLow', ''),
            'o': btc_info.get('regularMarketOpen', ''),
            'pc': btc_info.get('regularMarketPreviousClose', '')
        }
        return result
    except Exception as e:
        print(f"An error occurred in btcOtherDataFailSafe: {e}")
        return {key: '' for key in ['h', 'l', 'o', 'pc']}







def failsafe(symbol):
    try:
        # Get the current Unix timestamp
        current_time = int(time.time())
        # Subtract 1 minute (60 seconds) from the current time
        one_minute_ago = current_time - 500

        # Define the Yahoo Finance URL with the adjusted time for period1 and the current time for period2
        url = f'{env.finance_url}{symbol}?period1={one_minute_ago}&period2={current_time}&interval=1m&includePrePost=true&events=div%7Csplit%7Cearn&&lang=en-US&region=US'

        headers = {
            'accept': '*/*',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'en-US,en;q=0.9',
            'referer': 'https://www.google.com',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36 Edg/85.0.564.44'
        }

        # Send the GET request
        response = requests.get(url, headers=headers)

        # Check if the request was successful
        if response.status_code == 200:
            data = response.json()
            quote = data['chart']['result'][0]['indicators']['quote'][0]

            quote_variables = data['chart']['result'][0]['indicators']['quote'][0].keys()
            print(list(quote_variables))


            # Extract the last non-null value for each key
            result = {}
            for key in ['close']:
                last_non_null_value = None
                for value in reversed(quote[key]):
                    if value is not None:
                        last_non_null_value = value
                        break
                result[key[0]] = last_non_null_value  # Use first letter of each key for consistency with Finnhub response
            
            return result
        else:
            print(f"Failed to retrieve data from Yahoo Finance: {response.status_code}")
            return {key: '' for key in ['c', 'h', 'l', 'o', 'pc', 'v']} 
        
    except Exception as e:
        print(f"An error occurred in failsafe: {e}")
        return {key: '' for key in ['c', 'h', 'l', 'o', 'pc', 'v']}



def get_price(client, symbol):
    retry_count = 0
    max_retries = 2
    while retry_count < max_retries:
        price = client.quote(symbol)
        print(price)
        if price['c'] != 0:  # Check if the price is not zero
            return price
        else:
            print("retlying...")
            retry_count += 1
            #time.sleep(60)  # Wait for 60 seconds before retrying, to reset the limit

    if(symbol  == 'BTC-USD'):
        bttfailsafe = failsafe(symbol)
        return btcOtherDataFailSafe(symbol, bttfailsafe['c'])
    
    return failsafe(symbol) # Return None if max retries reached

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
        sys.exit(1)
        return

    # Create the directory if it does not exist
    os.makedirs('data/preprocessed/finance', exist_ok=True)

    # Get the current timestamp
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    timestamp_filename = timestamp.replace(" ", "_").replace(":", "-")

    # Define the JSON file path
    json_file = f'data/preprocessed/finance/finance_data_{timestamp_filename}.json'

    # Create a dictionary to hold the stock prices
    stock_data = {
        'timestamp': timestamp,
        'BTC Price': btc_price['c'],
        'BTC High': btc_price['h'],            # Highest price of Bitcoin during the trading day
        'BTC Low': btc_price['l'],             # Lowest price of Bitcoin during the trading day
        'BTC Open': btc_price['o'],            # Opening price of Bitcoin
        'BTC Previous Close': btc_price['pc'],
        'Crude Oil Price': crude_oil_price['c'],
        'Gold Price': gold_price['c'],
        'ETH Price': eth_price['c'],
        'MSFT Price': msft_price['c'],
        'JPM Price': jpm_price['c'],
        'JNJ Price': jnj_price['c'],
        'XOM Price': xom_price['c']
    }

    print(stock_data)

    # Write the dictionary to a JSON file
    with open(json_file, 'w', encoding='utf-8') as file:
        json.dump(stock_data, file, ensure_ascii=False, indent=4)

    print(f"Data written to {json_file}")

if __name__ == "__main__":
    main()
