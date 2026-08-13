# file_utils.py
import chardet
import pandas as pd
from io import StringIO

def read_file(file_path):
    try:
        with open(file_path, 'rb') as f:
            raw_data = f.read()
            encoding = chardet.detect(raw_data)['encoding']
        with open(file_path, 'r', encoding=encoding) as file:
            content = file.read().replace,('\n', ' ')
        return content
    except Exception as e:
        raise e

def read_csv_file(csv_file):
    try:
        raw_data = csv_file.read()
        encoding = chardet.detect(raw_data)['encoding']
        decoded_data = raw_data.decode(encoding)
        df = pd.read_csv(StringIO(decoded_data), on_bad_lines="skip")
        return df
    except Exception as e:
        raise e