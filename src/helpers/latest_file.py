import os
from datetime import datetime


def get_latest_file(directory):
    files = os.listdir(directory)
    if not files:
        return None
    
    latest_timestamp = None
    latest_file = None
    
    for file in files:
        if  file.endswith('.json'):
            parts = file.split('_')
            date_and_time = "_".join(parts[2:4])

            # Remove the ".json" extension
            timestamp_str = date_and_time[:-5]
            timestamp_str = timestamp_str.replace('-', ' ').replace('_', ' ')
            timestamp = datetime.strptime(timestamp_str, "%Y %m %d %H %M %S")
            
            if latest_timestamp is None or timestamp > latest_timestamp:
                latest_timestamp = timestamp
                latest_file = file
    
    if latest_file:
        return os.path.join(directory, latest_file), latest_timestamp
    else:
        return None