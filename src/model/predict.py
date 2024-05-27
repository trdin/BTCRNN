import joblib
import numpy as np
import pandas as pd
import tensorflow as tf
import json
from datetime import timedelta
import onnxruntime as ort
import src.model.prepare_data as pld
import src.model.train_multi_model as tm


def predict_multi(windowsize=8):

    model = ort.InferenceSession("./models/multi/model_production.onnx")
    btc_scaler = joblib.load("./models/multi/btc_scaler.joblib")

    data = pd.read_csv("./data/processed/finance_full_data.csv")

    learn_features, all_data, pipeline = pld.prepare_data(
        "./data/processed/finance_full_data.csv"
    )

    learn_features = learn_features[-windowsize:]

    print(learn_features)

    btc_data = np.array(learn_features[:, 0])
    btc_normalized = btc_scaler.transform(btc_data.reshape(-1, 1))

    data_normalized = np.column_stack([btc_normalized, np.array(learn_features[:, 1:])])

    look_back = windowsize
    step = 1

    X_final = data_normalized.reshape(
        1, data_normalized.shape[1], data_normalized.shape[0]
    )

    predicitons = model.run(["output"], {"input": X_final})[0]

    predicitons = btc_scaler.inverse_transform(predicitons)

    print("###############--Predictions--##############")
    print(predicitons)

    return predicitons
