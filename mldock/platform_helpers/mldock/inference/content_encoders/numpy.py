"""
    NUMPY CONTENT ENCODERS

    Handle Encoding of Content from numpy array in to appropriate format for response
"""
# Copyright 2018 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the 'License'). You
# may not use this file except in compliance with the License. A copy of
# the License is located at
#
#     http://aws.amazon.com/apache2.0/
#
# or in the 'license' file accompanying this file. This file is
# distributed on an 'AS IS' BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
# ANY KIND, either express or implied. See the License for the specific
# language governing permissions and limitations under the License.
# import csv
import io
import json

import numpy as np

def array_to_npy(array_like):
    """Convert an array-like object to the NPY format.
    To understand what an array-like object is, please see:
    https://docs.scipy.org/doc/numpy/user/basics.creation.html#converting-python-array-like-objects-to-numpy-arrays
    Args:
        array_like (np.array or Iterable or int or float): Array-like object to be converted to NPY.
    Returns:
        (obj): NPY array.
    """
    buffer = io.BytesIO()
    np.save(buffer, array_like)
    return buffer.getvalue()

def array_to_csv(array_like, quoted=True):
    """Convert an array like object to CSV.
    To understand what an array-like object is, please see:
    https://docs.scipy.org/doc/numpy/user/basics.creation.html#converting-python-array-like-objects-to-numpy-arrays
    Args:
        array_like (np.array or Iterable or int or float): Array-like object to be converted to CSV.
    Returns:
        (str): Object serialized to CSV.
    """
    data = np.array(array_like)
    if len(data.shape) == 1:
        data = np.reshape(data, (data.shape[0], 1))

    stream = io.StringIO()

    print(data)
    if quoted:
        np.savetxt(stream, data, delimiter=",", fmt='"%s"')
    else:
        np.savetxt(stream, data, delimiter=",", fmt='%s')
    return stream.getvalue()

def array_to_json(array_like):
    """
        Convert an array-like object to JSON.

        To understand what an array-like object is, please see:
        https://docs.scipy.org/doc/numpy/user/basics.creation.html#converting-python-array-like-objects-to-numpy-arrays
        Args:
            array_like (np.array or Iterable or int or float): Array-like object to be
                                                            converted to JSON.
        Returns:
            (str): Object serialized to JSON.
    """

    def default(_array_like):
        if hasattr(_array_like, "tolist"):
            return _array_like.tolist()
        return json.JSONEncoder().default(_array_like)

    return json.dumps(array_like, default=default)
