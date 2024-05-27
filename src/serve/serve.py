
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



def dowload_models():
    print("###############--Downloading models--##############")
    station_dir = f"models/multi"
    os.makedirs(station_dir, exist_ok=True)
    model = mc.download_model_onnx("multi", "production")
    btc_scaler = mc.download_scaler("multi", "btc_scaler", "production")

    joblib.dump(btc_scaler, os.path.join(station_dir, 'btc_scaler.joblib'))
        

def predict(data):
    try:
        required_features = ['date','available_bike_stands', 'temperature', 'relative_humidity',
             'apparent_temperature', 'dew_point', 'precipitation_probability',
               'surface_pressure']
        for obj in data:
            for feature in required_features:
                if feature not in obj:
                    return {'error': f'Missing feature: {feature}'}, 400

        prediction = pred.predict(data)

        return {'prediction': prediction.tolist()}
    except Exception as e:
        return {'error': str(e)}, 400

app = Flask(__name__)
CORS(app) 

@app.route('/predict', methods=['POST'])
def predict_air():
    data = request.get_json()
    result = predict(data)
    return jsonify(result)

@app.route('/predict', methods=['GET'])
def get_model():

    
    predictions = pred.predict_multi()
    #db.insert_prediciton(f"station_{station_id}", {'predictions': predictions, "date": datetime.datetime.now()})
    return jsonify({'prediction': float(predictions[0][0])})

    
    


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