import os
import json
import yfinance as yf
import src.helpers.latest_file as lf
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

def read_articles_and_predict():
    # Load the articles data from the JSON file
    latest_file, timestamp = lf.get_latest_file('data/raw')
    with open(latest_file, 'r', encoding='utf-8') as f:
        articles_data = json.load(f)

    # Load the tokenizer and model
    print("Loading the tokenizer and model...")
    tokenizer = AutoTokenizer.from_pretrained("ProsusAI/finbert")
    model = AutoModelForSequenceClassification.from_pretrained("ProsusAI/finbert")
    print("Model loaded successfully!\n")
    
    # Define the sentiment labels
    sentiment_labels = ["Negative", "Neutral", "Positive"]
    
    # List to hold the predictions
    predictions_data = []

    for article in articles_data:
        title = article['title']
        link = article['link']
        content = title + "\n" + article['content']

        # Tokenize the content
        inputs = tokenizer(content, return_tensors='pt', truncation=True, padding=True, max_length=512)

        # Predict using the model
        outputs = model(**inputs)
        predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
        predicted_class = predictions.argmax().item()

        # Get the sentiment label
        sentiment = sentiment_labels[predicted_class]

        # Print the prediction
        print(f"Title: {title}")
        print(f"Link: {link}")
        print(f"Predicted sentiment: {sentiment}\n")

        # Append prediction to the list
        predictions_data.append({
            'title': title,
            'link': link,
            'predicted_sentiment': sentiment,
            'predicted_class': predicted_class,
        })

    # Create the directory if it doesn't exist
    os.makedirs('data/preprocessed/articles', exist_ok=True)


    print(predictions_data)

    timestamp =  timestamp.strftime("%Y-%m-%d %H:%M:%S").replace(" ", "_").replace(":", "-")
    
    # Write the predictions data to a JSON file
    predictions_file = os.path.join('data/preprocessed/articles', f'predictions_data_{timestamp}.json')
    with open(predictions_file, 'w', encoding='utf-8') as f:
        json.dump(predictions_data, f, ensure_ascii=False, indent=4)
    print(f"Predictions saved to {predictions_file}")

def main():
    read_articles_and_predict()

if __name__ == "__main__":
    main()