
import mlflow
import dagshub.auth
import dagshub
import src.enviorment_variables as settings

import src.database.connector as db
import os
import pandas as pd
from datetime import timedelta
from sklearn.metrics import mean_absolute_error, mean_squared_error, explained_variance_score


def predictions_test(model_name, finance_data):
    
    print("##############"+ model_name + "##############")
    predictions_data = db.preditcions_today(model_name)

    if not predictions_data:
        print("No predictions for today for station ", model_name)
        mlflow.end_run()
        return
    mlflow.start_run(run_name=model_name, experiment_id="1")

    #station_data = station_data.set_index(['date'])
    mapped_predictions = []
    
    for pred_obj in predictions_data:
        pred = pred_obj['price']
        date = pd.to_datetime(pred_obj['timestamp'])
        finance_data.reset_index(inplace=True)
        finance_data = finance_data.set_index(['date'])
        
        target_time= date
        nearest_timestamp_index = finance_data.index.get_indexer(
            [target_time],
            method='nearest'
        )[0]

            
        row_with_nearest_timestamp = finance_data.iloc[nearest_timestamp_index].to_dict()

        # Append the mapped prediction to the list
        mapped_predictions.append({
            'date': target_time,
            'prediction': pred,
            'true': row_with_nearest_timestamp['BTC Price']
        })


    y_true = [x['true'] for x in mapped_predictions]
    y_pred = [x['prediction'] for x in mapped_predictions]

    mae = mean_absolute_error(y_true, y_pred)
    mse = mean_squared_error(y_true, y_pred)
    evs = explained_variance_score(y_true, y_pred)

    # Save the result into mlflow as an experiment
    mlflow.log_metric("mae", mae)
    mlflow.log_metric("mse", mse)
    mlflow.log_metric("evs", evs)

    mlflow.end_run()

def main():
    dagshub.auth.add_app_token(token=settings.mlflow_tracking_password)
    dagshub.init('BTCRNN', settings.mlflow_tracking_username, mlflow=True)
    mlflow.set_tracking_uri(settings.mlflow_tracking_uri)
    
    
   

    data = pd.read_csv("./data/processed/finance_full_data.csv")

    data['date'] = pd.to_datetime(data['date'])
    data.sort_values(by='date', inplace=True)
    data.drop_duplicates('date', inplace=True)
    data.reset_index(inplace=True)
    data = data.set_index(['date'])

    predictions_test("multi", data)

        

if __name__ == '__main__':
    main()