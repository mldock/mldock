"""
    DATAFRAME CONTENT DECODERS

    Handle Decoding of Content in to appropriate format from request as pandas dataframe.

    e.g.
        list of lists -> pd.DataFrame.
"""
import io
import json
import pandas as pd

def csv_to_pandas(bytes_like: bytes):
    """
        Decodes byte encoded csv to pandas dataframe.

        args:
            bytes_like (str): bytes serialized CSV string.
        return:
            (pd.DataFrame): data as pandas dataframe
    """
    string_like = bytes_like.decode()
    data = io.StringIO(string_like)
    return pd.read_csv(data)

def json_list_to_pandas(json_data):
    """
        Transforms a array of flat json objects in to pandas dataframe.

        args:
            json_data (str): data as json serialized list of dictionaries.
        return:
            (pd.DataFrame): data as pandas dataframe
    """
    data = json.loads(json_data)
    return pd.DataFrame(data)
