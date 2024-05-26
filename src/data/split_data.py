# src/data/split_data.py
import os
import pandas as pd

def split_train_test(data):
    # Sort data by date (assuming there's a column named 'date')
    data_sorted = data.sort_values(by='date')

    # Calculate the index to split the data (10% for test)
    split_index = int(0.1 * len(data_sorted))

    # Split data into train and test sets
    test_data = data_sorted.iloc[-split_index:]
    train_data = data_sorted.iloc[:-split_index]

    return train_data, test_data

def main():
    # Define the directory containing the CSV files
    data_directory = "./data/processed/"

    # Loop through each station number from 1 to 29

    # Read the CSV file
    file_path = os.path.join(data_directory, "finance_full_data.csv")
    data = pd.read_csv(file_path)

    # Split data into train and test sets
    train_data, test_data = split_train_test(data)

    # Save train and test sets to CSV files
    train_file_path = os.path.join(data_directory, f"train_data.csv")
    test_file_path = os.path.join(data_directory, f"test_data.csv")

    train_data.to_csv(train_file_path, index=False)
    test_data.to_csv(test_file_path, index=False)

    print("Data split into train and test sets successfully!")

if __name__ == "__main__":
    main()