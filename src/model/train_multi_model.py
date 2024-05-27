# %%
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import tensorflow as tf
from tensorflow.keras.layers import LSTM, Dense 
from tensorflow.keras.models import Sequential
import joblib
import src.model.prepare_data as pld
import src.visualization.visualization as vis
import os
import mlflow
import dagshub.auth
import dagshub
from mlflow import MlflowClient
from mlflow.onnx import log_model as log_onnx_model
import src.remote.mlflow_client as mc
from mlflow.onnx import log_model as log_onnx_model
import tf2onnx
from mlflow.models import infer_signature
import onnxruntime as ort

import src.enviorment_variables as env


def mlflow_save_onnx(model, mode, client,  feature_number,window_size, X_test):
    model.output_names = ["output"]

    input_signature = [
        tf.TensorSpec(shape=(None, window_size, feature_number), dtype=tf.double, name="input")
    ]

    onnx_model, _ = tf2onnx.convert.from_keras(model=model, input_signature=input_signature, opset=13)

    station_model = log_onnx_model(onnx_model=onnx_model,
                            artifact_path=f"models/{mode}/model",
                            signature=infer_signature(X_test, model.predict(X_test)),
                            registered_model_name=f"model={mode}")

    
    metadata = {
        "station_name": mode,
        "model_type": "LSTM",
        "input_shape": model.input_shape,
        "output_shape": model.output_shape,
    }

    """ station_model = mlflow.onnx.log_model(
            onnx_model=model,
            artifact_path=f"models/{station_name}/model",
            registered_model_name=f"model={station_name}",
        ) """
    
    model_version = client.create_model_version(
            name=f"model={mode}",
            source=station_model.model_uri,
            run_id=station_model.run_id
        )

    client.transition_model_version_stage(
        name=f"model={mode}",
        version=model_version.version,
        stage="staging",
    )



def save_train_metrics(history, file_path):
    with open(file_path, 'w') as file:
        file.write("Epoch\tTrain Loss\tValidation Loss\n")
        for epoch, (train_loss, val_loss) in enumerate(zip(history.history['loss'], history.history['val_loss']), start=1):
            file.write(f"{epoch}\t{train_loss}\t{val_loss}\n")

def save_test_metrics(mae, mse, evs, file_path):
    with open(file_path, 'w') as file:
        file.write("Model Metrics\n")
        file.write(f"MAE: {mae}\n")
        file.write(f"MSE: {mse}\n")
        file.write(f"EVS: {evs}\n")

def build_lstm_model(input_shape):
    model = Sequential()
    model.add(LSTM(units=32, return_sequences=True, input_shape=input_shape))
    model.add(LSTM(units=32))
    model.add(Dense(units=16, activation='relu'))
    model.add(Dense(units=1))

    return model

def train_model(model, X_train, y_train, epochs=50, mode = "default", batch_size=32):
    model.compile(optimizer='adam', loss='mean_squared_error')
    history = model.fit(X_train, y_train, epochs=epochs, batch_size=batch_size, validation_split=0.2, verbose=1)
    vis.plot_model_history(history)

def create_multivariate_dataset_with_steps(time_series, look_back=1, step=1):
    X, y = [], []
    for i in range(0, len(time_series) - look_back, step):
        X.append(time_series[i:(i + look_back), :])
        y.append(time_series[i + look_back, 0]) 
    return np.array(X), np.array(y)


def copy_station_names_to_file(data):
    try:
        for station in data:
            source_filename = 'data/processed/' + station['name'] + '.csv'
            destination_filename = 'data/processed/' + station['number'] + '.csv'
            if os.path.exists(source_filename):
                os.rename(source_filename, destination_filename)
            else:
                print(f"Source file {source_filename} does not exist.")
    except Exception as e:
        print(f"An error occurred while copying station files: {e}")





    
   
def ensure_directory_exists(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def train(data_path, mode,windowsize = 8 ):

    dagshub.auth.add_app_token(token=env.mlflow_tracking_password)
    dagshub.init('BTCRNN', env.mlflow_tracking_username, mlflow=True)
    mlflow.set_tracking_uri(env.mlflow_tracking_uri)

    client = MlflowClient()
    
    mlflow.start_run(run_name=mode, experiment_id="0")
    
    mlflow.tensorflow.autolog()

    learn_features, all_data, pipeline = pld.prepare_data(data_path)

    mc.save_pipline(pipeline, mode, client)
    



    

    btc_scaler = MinMaxScaler()
    

    train_final_stands = np.array(learn_features[:, 0])
    train_final_stands_normalized = btc_scaler.fit_transform(train_final_stands.reshape(-1, 1))

   

    train_final_other = np.array(learn_features[:, 1:])




    train_final_normalized = np.column_stack([train_final_stands_normalized, train_final_other])

    
    look_back = windowsize
    step = 1


    X_final, y_final = create_multivariate_dataset_with_steps(train_final_normalized, look_back, step)

    print("###############SHAPE################")
    print(f"X_train shape: {X_final.shape}")
    X_final = X_final.reshape(X_final.shape[0], X_final.shape[2], X_final.shape[1])

    print("###############SHAPE################")
    print(f"X_train shape: {X_final.shape}")
    

    input_shape = ( X_final.shape[1],  X_final.shape[2])


    

    lstm_model_final = build_lstm_model(input_shape)

    epochs = 10
    batch_size = 32


    train_model(lstm_model_final, X_final, y_final, epochs=10, batch_size=32)

    mc.mlflow_save_scaler(client, "btc_scaler", btc_scaler, mode)
    #mc.mlflow_save_scaler(client, "other_scaler", other_scaler, station_name)


    mlflow.log_param("epochs", epochs)
    mlflow.log_param("batch_size", batch_size)
    mlflow.log_param("train_dataset_size", len(X_final))
    #mc.mlflow_save_model(lstm_model_final, station_name, client)
    mlflow_save_onnx(lstm_model_final, mode, client, 8, 15, X_final)


    station_directory = './models/' + mode
    ensure_directory_exists(station_directory)

    """ lstm_model_final.save(os.path.join(station_directory, 'model.h5'))

    joblib.dump(btc_scaler, os.path.join(station_directory, 'btc_scaler.joblib'))
    joblib.dump(other_scaler, os.path.join(station_directory, 'other_scaler.joblib')) """

    mlflow.end_run()



def main():
    train("./data/processed/train_data.csv", "multi")

if __name__ == '__main__':
    main()