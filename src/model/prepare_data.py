import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import MinMaxScaler
from sklearn.ensemble import RandomForestRegressor

def prepare_data(path_to_data):
    # Read the data
    all_data = pd.read_csv(path_to_data)
    print(all_data.head())

    # Define the pipeline with a scaler and model
    pipeline = Pipeline(steps=[
        ("scaler", MinMaxScaler()),
        ("model", RandomForestRegressor())
    ])

    # Parse the date column and sort by date
    all_data['date'] = pd.to_datetime(all_data['date'])
    all_data.sort_values(by='date', inplace=True)

    # Resample the data to hourly frequency and handle missing values
    all_data.set_index('date', inplace=True)
    all_data = all_data.resample('20T').mean()
    all_data.reset_index(inplace=True)

    print(all_data.head())

    print("\nMissing values before dropping NaNs:")
    print(all_data.isnull().sum())
    all_data = all_data.dropna()

    print("size")
    print(len(all_data))

    # Define the relevant features
    features = [
        'BTC Price', 'BTC High', 'BTC Low', 'BTC Open', 'BTC Previous Close',
        'Crude Oil Price', 'Gold Price', 'ETH Price', 'MSFT Price', 'JPM Price',
        'JNJ Price', 'XOM Price', 'Sentiment Article 1', 'Sentiment Article 2', 'Sentiment Article 3'
    ]
    all_data = all_data[['date'] + features]

    # Check for missing values
    missing_values = all_data.isnull().sum()
    print(missing_values)

    # Identify columns with missing values
    features_with_missing_values = missing_values[missing_values > 0].index
    columns_with_missing_values = all_data.columns[all_data.isnull().any()].tolist()
    columns_complete_values = all_data.drop(columns_with_missing_values + ["date"], axis=1).columns.tolist()

    # Split data into complete and missing value subsets
    missing_df = all_data[all_data.isnull().any(axis=1)]
    complete_df = all_data.dropna()

    # Impute missing values using the pipeline
    for column in columns_with_missing_values:
        X = complete_df[columns_complete_values]
        y = complete_df[column]
        
        pipeline.fit(X, y)
        
        missing_X = missing_df[columns_complete_values]
        predictions = pipeline.predict(missing_X)
        
        all_data.loc[missing_df.index, column] = predictions

    # Check for any remaining missing values
    missing_values = all_data.isnull().sum()
    print(missing_values)

    # Select features for learning
    selected_features = [
        'BTC High', 'BTC Low', 'BTC Open', 'BTC Previous Close',
        'Crude Oil Price', 'Gold Price', 'ETH Price', 'MSFT Price', 'JPM Price',
        'JNJ Price', 'XOM Price', 'Sentiment Article 1', 'Sentiment Article 2', 'Sentiment Article 3'
    ]

    learn_features = all_data[['BTC Price'] + selected_features]  # 'BTC Price' is chosen as the target variable for this example
    learn_features = learn_features.values
    return learn_features, all_data, pipeline

