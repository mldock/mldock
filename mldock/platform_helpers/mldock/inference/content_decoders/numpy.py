"""
    NUMPY CONTENT DECODERS

    Handle Decoding of Content in to appropriate format from request as numpy array.

    e.g. 
        list of lists -> np.array.
"""
import csv
import io
import json
from PIL import Image
import numpy as np

from mldock.platform_helpers.mldock.inference import content_types

def image_to_numpy(image_bytes):
    """Convert an image bytes string into numpy through PIL.
    Args:
        bytes_like (str): bytes serialized image string.
    Returns:
        (np.array): Converted numpy array.
    """
    pillow_image =  Image.open(
        io.BytesIO(image_bytes)
    ).convert('L')
    return np.asarray(pillow_image)

def npy_to_numpy(npy_array):
    """Convert an NPY array into numpy.
    Args:
        npy_array (npy array): NPY serialized array to be converted.
    Returns:
        (np.array): Converted numpy array.
    """
    stream = io.BytesIO(npy_array)
    return np.load(stream, allow_pickle=True)

def json_to_numpy(json_data):
    """
        Convert a JSON object to a numpy array.

        Args:
            string_like (str): JSON serialized data.
        Returns:
            (np.array): data as Numpy array.
    """
    data = json.loads(json_data)
    return np.array(data)

def csv_to_numpy(bytes_like):
    """
        Convert a CSV object to a numpy array.

        Args:
            bytes_like (str): bytes serialized CSV string.
        Returns:
            (np.array): data as Numpy array.
    """
    try:
        stream = io.StringIO(bytes_like.decode())
        reader = csv.reader(stream, delimiter=",", quotechar='"', doublequote=True, strict=True)
        data = np.array([row for row in reader]).squeeze()
        return data

    except ValueError as e:
        if dtype is not None:
            raise Exception(
                "Error while writing numpy array: {}. dtype is: {}".format(e, dtype)
            )
        raise
    except Exception as e:
        raise Exception("Error while decoding csv: {}".format(e))
