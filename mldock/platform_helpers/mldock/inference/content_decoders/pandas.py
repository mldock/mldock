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

def csv_to_pandas(bytes_like: bytes, dtype=None):
    """Decodes byte encoded csv to pandas dataframe"""
    s = bytes_like.decode()
    data = io.StringIO(s)
    return pd.read_csv(data).astype(dtype)

def json_list_to_pandas(json_data, dtype=None):
    """Transforms a array of flat json objects in to pandas dataframe"""
    data = json.loads(json_data)
    return pd.DataFrame(data).astype(dtype)

_decoders_map = {
    content_types.CSV: csv_to_pandas,
    content_types.JSON: json_list_to_pandas,
}

def decode(obj, content_type: str):
    """Decode an object of one of the default content types to a numpy array.
    Args:
        obj (object): Object to be decoded.
        content_type (str): Content type to be used.
    Returns:
        np.array: Decoded object.
    """
    try:
        decoder = _decoders_map[content_type]
        return decoder(obj)
    except KeyError:
        raise TypeError(
            "{content_type} is not "
            "supported for pandas decode.".format(
                content_type=content_type
            )
        )

