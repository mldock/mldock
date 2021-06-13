"""
    NUMPY CONTENT DECODERS

    Handle Decoding of Content in to appropriate format from request as numpy array.

    e.g. 
        list of lists -> np.array.
"""
import csv
import io
import json
import numpy as np

from mldock.platform_helpers.mldock.inference import content_types

def npy_to_numpy(npy_array):
    """Convert an NPY array into numpy.
    Args:
        npy_array (npy array): NPY array to be converted.
    Returns:
        (np.array): Converted numpy array.
    """
    stream = io.BytesIO(npy_array)
    return np.load(stream, allow_pickle=True)

def json_to_numpy(string_like, dtype=None):
    """Convert a JSON object to a numpy array.
        Args:
            string_like (str): JSON string.
            dtype (dtype, optional):  Data type of the resulting array. If None,
                                      the dtypes will be determined by the
                                      contents of each column, individually.
                                      This argument can only be used to
                                      'upcast' the array.  For downcasting,
                                      use the .astype(t) method.
        Returns:
            (np.array): Numpy array.
        """
    data = json.loads(string_like)
    return np.array(data, dtype=dtype)

def csv_to_numpy(string_like, dtype=None):
    """Convert a CSV object to a numpy array.
    Args:
        string_like (str): CSV string.
        dtype (dtype, optional):  Data type of the resulting array. If None, the
                                  dtypes will be determined by the contents of
                                  each column, individually. This argument can
                                  only be used to 'upcast' the array.  For
                                  downcasting, use the .astype(t) method.
    Returns:
        (np.array): Numpy array.
    """
    try:
        stream = io.StringIO(string_like.decode())
        reader = csv.reader(stream, delimiter=",", quotechar='"', doublequote=True, strict=True)
        data = np.array([row for row in reader], dtype=dtype).squeeze()
        return data

    except ValueError as e:
        if dtype is not None:
            raise Exception(
                "Error while writing numpy array: {}. dtype is: {}".format(e, dtype)
            )
        raise
    except Exception as e:
        raise Exception("Error while decoding csv: {}".format(e))

_decoders_map = {
    content_types.NPY: npy_to_numpy,
    content_types.CSV: csv_to_numpy,
    content_types.JSON: json_to_numpy,
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
            "supported for numpy decode.".format(
                content_type=content_type
            )
        )
