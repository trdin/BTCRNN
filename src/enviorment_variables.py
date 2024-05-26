import os
from dotenv import load_dotenv

load_dotenv()

finnhub_api_key = os.getenv("FINNHUB_API_KEY")


mlflow_tracking_uri = os.getenv("MLFLOW_TRACKING_URI")
mlflow_tracking_username = os.getenv("MLFLOW_TRACKING_USERNAME")
mlflow_tracking_password = os.getenv("MLFLOW_TRACKING_PASSWORD")

finance_url = os.getenv("FINANCE_URL")
