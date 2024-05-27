import numpy as np
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.layers import LSTM, Dense
from tensorflow.keras.models import Sequential
import tensorflow as tf
import joblib
import src.model.prepare_data as pld
import src.helpers.calculate as calc
import src.visualization.visualization as vis
import os
import mlflow
import dagshub.auth
import dagshub
from mlflow import MlflowClient
import src.model.train_multi_model as tm
import src.remote.mlflow_client as mc

import src.enviorment_variables as env
import onnxruntime as ort


def evaluate_model(data_path, mode, windowsize=8):

    dagshub.auth.add_app_token(token=env.mlflow_tracking_password)
    dagshub.init('BTCRNN', env.mlflow_tracking_username, mlflow=True)
    mlflow.set_tracking_uri(env.mlflow_tracking_uri)

    mlflow.start_run(run_name=mode, experiment_id="0", nested=True)

    mlflow.tensorflow.autolog()

    model = mc.download_model_onnx(mode, "staging")
    btc_scaler = mc.download_scaler(mode, "btc_scaler", "staging")
    pipeline = mc.download_pipeline(mode, "staging")
    # other_scaler = mc.download_scaler(mode, "other_scaler", "staging")

    # dowload for produciton
    prod_model = mc.download_model_onnx(mode, "production")
    prod_btc_scaler = mc.download_scaler(mode, "btc_scaler", "production")
    pipeline = mc.download_pipeline(mode, "production")

    # prod_other_scaler = mc.download_scaler(mode, "other_scaler", "production")

    if model is None or btc_scaler is None:  # TODO replace with pipeline
        print(f"Model or scaler was not downloaded properly. Skipping {mode}")
        mlflow.end_run()
        return

    if prod_model is None or prod_btc_scaler is None:
        mc.prod_model_save(mode)
        print(
            f"Production model does not exist. Replacing with latest staging model. Skipping evaluation."
        )
        mlflow.end_run()
        return

    # https://stackoverflow.com/questions/71279968/getting-a-prediction-from-an-onnx-model-in-python
    model = ort.InferenceSession(model)
    prod_model = ort.InferenceSession(prod_model)

    learn_features, all_data, pipeline = pld.prepare_data(data_path)
    # mc.save_pipline(pipeline, station_name)

    stands_data = np.array(learn_features[:, 0])
    stands_normalized = btc_scaler.transform(stands_data.reshape(-1, 1))
    prod_stands_normalized = prod_btc_scaler.transform(stands_data.reshape(-1, 1))

    """ other_data = np.array(learn_features[:, 1:])
    other_normalized = other_scaler.transform(other_data)
    prod_other_normalized = prod_other_scaler.transform(other_data) """

    data_normalized = np.column_stack(
        [stands_normalized, np.array(learn_features[:, 1:])]
    )
    prod_data_normalized = np.column_stack(
        [prod_stands_normalized, np.array(learn_features[:, 1:])]
    )

    look_back = windowsize
    step = 1

    X_final, y_final = tm.create_multivariate_dataset_with_steps(
        data_normalized, look_back, step
    )
    prod_X_final, prod_y_final = tm.create_multivariate_dataset_with_steps(
        prod_data_normalized, look_back, step
    )

    print(X_final.shape)

    X_final = X_final.reshape(X_final.shape[0], X_final.shape[2], X_final.shape[1])
    prod_X_final = prod_X_final.reshape(
        prod_X_final.shape[0], prod_X_final.shape[2], prod_X_final.shape[1]
    )

    print("###############SHAPE################")
    print(X_final.shape)

    y_test_predicitons = model.run(["output"], {"input": X_final})[0]
    prod_y_test_predicitons = prod_model.run(["output"], {"input": X_final})[0]

    y_test_true = btc_scaler.inverse_transform(y_final.reshape(-1, 1))
    prod_y_test_true = prod_btc_scaler.inverse_transform(prod_y_final.reshape(-1, 1))

    y_test_predicitons = btc_scaler.inverse_transform(y_test_predicitons)
    prod_y_test_predicitons = prod_btc_scaler.inverse_transform(prod_y_test_predicitons)

    lstm_mae_adv, lstm_mse_adv, lstm_evs_adv = calc.calculate_metrics(
        y_test_true, y_test_predicitons
    )
    prod_lstm_mae_adv, prod_lstm_mse_adv, prod_lstm_evs_adv = calc.calculate_metrics(
        prod_y_test_true, prod_y_test_predicitons
    )
    print(
        f"Staging Model Metrics: MAE={lstm_mae_adv}, MSE={lstm_mse_adv}, EVS={lstm_evs_adv}"
    )
    print(
        f"Prod Model Metrics: MAE={prod_lstm_mae_adv}, MSE={prod_lstm_mse_adv}, EVS={prod_lstm_evs_adv}"
    )

    mlflow.log_metric("MSE_staging", lstm_mse_adv)
    mlflow.log_metric("MAE_staging", lstm_mae_adv)
    mlflow.log_metric("EVS_staging", lstm_evs_adv)

    mlflow.log_metric("MSE_production", prod_lstm_mse_adv)
    mlflow.log_metric("MAE_production", prod_lstm_mae_adv)
    mlflow.log_metric("EVS_production", prod_lstm_evs_adv)

    tm.ensure_directory_exists("./reports/" + mode)
    tm.save_test_metrics(
        lstm_mae_adv, lstm_mse_adv, lstm_evs_adv, "./reports/" + mode + "/metrics.txt"
    )

    if (
        prod_lstm_mse_adv > lstm_mse_adv
        and prod_lstm_mae_adv > lstm_mae_adv
        and prod_lstm_evs_adv < lstm_evs_adv
    ):
        print("REPLACING THE MODEL")
        mc.prod_model_save(mode)

    mlflow.end_run()


def main():

    evaluate_model("./data/processed/test_data.csv", "multi", windowsize=8)


if __name__ == "__main__":
    main()
