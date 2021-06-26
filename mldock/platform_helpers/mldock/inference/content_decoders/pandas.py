"""
    DATAFRAME CONTENT DECODERS

    Handle Decoding of Content in to appropriate format from request as pandas dataframe.

    e.g. 
        list of lists -> pd.DataFrame.
"""
import io
import json
import pandas as pd

from mldock.platform_helpers.mldock.inference import content_types

def csv_to_pandas(bytes_like: bytes):
    """
        Decodes byte encoded csv to pandas dataframe.

        args:
            bytes_like (str): bytes serialized CSV string.
        return:
            (pd.DataFrame): data as pandas dataframe
    """
    s = bytes_like.decode()
    data = io.StringIO(s)
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


