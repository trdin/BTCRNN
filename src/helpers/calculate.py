from sklearn.metrics import mean_absolute_error, mean_squared_error, explained_variance_score



def calculate_metrics(y_test, y_pred):
        mae = mean_absolute_error(y_test, y_pred)
        mse = mean_squared_error(y_test, y_pred)
        evs = explained_variance_score(y_test, y_pred)
        return mae, mse, evs
