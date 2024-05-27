
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import src.model.predict as pred
import src.remote.mlflow_client as mc
import joblib
import src.enviorment_variables as env
import mlflow
import dagshub.auth
import dagshub
import datetime
import subprocess
import csv
import json
from datetime import datetime, timedelta
import src.database.connector as db


last_task_time = None

def dowload_models():
    print("###############--Downloading models--##############")
    station_dir = f"models/multi"
    os.makedirs(station_dir, exist_ok=True)
    model = mc.download_model_onnx("multi", "production")
    btc_scaler = mc.download_scaler("multi", "btc_scaler", "production")

    joblib.dump(btc_scaler, os.path.join(station_dir, 'btc_scaler.joblib'))

def task():
    global last_task_time
    print("Running scheduled task... ########")
    # Run git pull
    subprocess.run(["git", "pull"]) #git pull -X theirs
    # Run dvc pull
    subprocess.run(["dvc", "pull", "-r", "origin", "--force"])
    # Update the last task time
    last_task_time = datetime.now()

def schedule_task():
    global last_task_time
    if last_task_time is None or (datetime.now() - last_task_time).total_seconds() > 1200:  # 20 minutes in seconds
        task()

def get_bitcoin_prices_with_timestamp(filename):
    # Get today's date in UTC
    today = datetime.utcnow().date()
    # Calculate yesterday's date in UTC
    yesterday = today - timedelta(days=1)
    # Initialize a dictionary to store Bitcoin prices with timestamps
    bitcoin_prices_with_timestamp = []

    with open(filename, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            # Convert date string to datetime object in UTC
            date = datetime.strptime(row['date'], '%Y-%m-%d %H:%M:%S').date()
            # Check if the date is within the range of yesterday to today
            if yesterday <= date <= today:
                bitcoin_prices_with_timestamp.append({
                    'timestamp': row['date'],
                    'price': float(row['BTC Price'])
                })

    return bitcoin_prices_with_timestamp
        

app = Flask(__name__)
CORS(app) 

@app.route('/btc', methods=['GET'])
def get_btc():
    filename = 'data/processed/finance_full_data.csv'
    bitcoin_prices_with_timestamp = get_bitcoin_prices_with_timestamp(filename)
    return jsonify(bitcoin_prices_with_timestamp)

@app.route('/predict', methods=['GET'])
def get_model():
    predictions, timestamp = pred.predict_multi()
    db.insert_prediciton("multi", {'price': float(predictions[0][0]),
                     'timestamp': timestamp.strftime("%Y-%m-%d %H:%M:%S")})
    return jsonify([{'price': float(predictions[0][0]),
                     'timestamp': timestamp.strftime("%Y-%m-%d %H:%M:%S")}])

@app.before_request
def before_request():
    schedule_task()


def main():
    print("###############--Starting server--##############")
    dagshub.auth.add_app_token(token=env.mlflow_tracking_password)
    dagshub.init('BTCRNN', env.mlflow_tracking_username, mlflow=True)
    mlflow.set_tracking_uri(env.mlflow_tracking_uri)
    dowload_models()


    app.run(host='0.0.0.0', port=3001)
    

if __name__ == '__main__':
    main()



""" "command = ["git", "pull"]
    
    # Run the command
    result = subprocess.run(command, capture_output=False, text=True)

    command = ["dvc", "pull", "-r", "origin", "--force"]
    
    # Run the command
    result = subprocess.run(command, capture_output=False, text=True)
" """