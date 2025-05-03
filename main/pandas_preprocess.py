import pandas as pd

def preprocess_data(data):
    for col in data.select_dtypes(include=['object']):
        data[col] = data[col].str.lower()
    return data

def clean_data(data):
    data = data.dropna()
    data = data.drop_duplicates()
    return data