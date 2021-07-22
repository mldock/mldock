"""
    NUMPY CONTENT DECODERS

    Handle Decoding of Content in to appropriate format from request as numpy array.

    e.g.
        list of lists -> np.array.
"""
import io
from PIL import Image
import numpy as np

def image_to_numpy(image_bytes, convert: str = None):
    """Convert an image bytes string into numpy through PIL.
    Args:
        bytes_like (str): bytes serialized image string.
        convert (str): pillow image convert mode
    Returns:
        (np.array): Converted numpy array.
    """
    pillow_image =  Image.open(
        io.BytesIO(image_bytes)
    )
    if convert is not None:
        pillow_image = pillow_image.convert(convert)
    return np.asarray(pillow_image)
