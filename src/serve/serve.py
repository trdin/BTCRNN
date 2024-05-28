
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
import pandas as pd


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
    
    # Reset any local changes
    try:
        subprocess.run(["git", "reset", "--hard", "origin/main"], check=True)
        print("Git reset completed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error during git reset: {e}")
    
    # Run git pull to fetch the latest changes
    try:
        subprocess.run(["git", "pull", "origin", "main"], check=True)
        print("Git pull completed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error during git pull: {e}")
    
    # Run dvc pull with --force
    try:
        subprocess.run(["poetry", "run", "dvc", "pull", "-r", "origin", "--force"], check=True)
        print("DVC pull completed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error during dvc pull: {e}")
    
    # Update the last task time
    last_task_time = datetime.now()
    print(f"Task completed at {last_task_time}")

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
                     'timestamp': timestamp})
    return jsonify([{'price': float(predictions[0][0]),
                     'timestamp': timestamp.strftime("%Y-%m-%d %H:%M:%S")}])


@app.route('/eval', methods=['GET'])
def get_acc():
    client = mlflow.tracking.MlflowClient()

    # Define the experiment ID
    experiment_id = "0"

    # Search for runs in the specified experiment with the filter
    runs = client.search_runs(
        experiment_ids=[experiment_id],
        order_by=["attributes.end_time DESC"]  # Order runs by end time descending
    )

    metrics_data_list = []

    # Extract metrics for each run and store them in a list of dictionaries
    for run in runs:
        metrics = run.data.metrics
        if all([
            metrics.get("MSE_staging") is not None,
            metrics.get("MAE_staging") is not None,
            metrics.get("EVS_staging") is not None,
            metrics.get("MSE_production") is not None,
            metrics.get("MAE_production") is not None,
            metrics.get("EVS_production") is not None
        ]):
            metrics_data_list.append({
                "run_id": run.info.run_id,
                "end_time": pd.to_datetime(run.info.end_time, unit='ms').isoformat(),
                "MSE_staging": metrics.get("MSE_staging"),
                "MAE_staging": metrics.get("MAE_staging"),
                "EVS_staging": metrics.get("EVS_staging"),
                "MSE_production": metrics.get("MSE_production"),
                "MAE_production": metrics.get("MAE_production"),
                "EVS_production": metrics.get("EVS_production")
            })

    # Replace 'model_name' with the name of your model
    mode = "multi"
    model_name = f"model={mode}"

    # Fetch the latest production version of the model
    model_versions = client.get_latest_versions(model_name, stages=["production"])
    production_metrics = {}
    if model_versions:
        production_model_version = model_versions[0]  # Assuming the latest version in Production
        run_id = production_model_version.run_id

        # Fetching the metrics for the run
        metrics = client.get_run(run_id).data.metrics
        production_metrics = client.get_run(run_id).data.metrics
    # Prepare the final JSON response
    response = {
        "current_production_model_metrics": production_metrics,
        "metrics": metrics_data_list
    }

    return jsonify(response)


@app.route('/prodeval', methods=['GET'])
def get_prodeval():
    client = mlflow.tracking.MlflowClient()

    # Define the experiment ID
    experiment_id = "1"

    # Search for runs in the specified experiment with the filter
    runs = client.search_runs(
        experiment_ids=[experiment_id],
        order_by=["attributes.end_time DESC"]  # Order runs by end time descending
    )

    metrics_data_list = []

    # Extract metrics for each run and store them in a list of dictionaries
    for run in runs:
        metrics = run.data.metrics
        if all([
            metrics.get("mse") is not None,
            metrics.get("evs") is not None,
            metrics.get("mae") is not None
        ]):
            metrics_data_list.append({
                "run_id": run.info.run_id,
                "end_time": pd.to_datetime(run.info.end_time, unit='ms').isoformat(),
                "mae": metrics.get("mae"),
                "mse": metrics.get("mse"),
                "evs": metrics.get("evs"),
            })

    # Prepare the final JSON response
    response = {
        "metrics": metrics_data_list
    }

    return jsonify(response)

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