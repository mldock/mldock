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
#
# Disclaimer: This code can be found here: https://github.com/aws/sagemaker-training-toolkit/blob/master/test/unit/test_encoder.py
#
import io
import pytest
import numpy as np
from PIL import Image

from mldock.platform_helpers.mldock.inference.content_decoders.image import (
    numpy as numpy_image_decoders,
)


@pytest.fixture
def image_bytes():
    """reads image as bytes string"""
    with open("tests/api/fixtures/eight.png", "rb") as file_:
        return file_.read()


@pytest.fixture
def image_array():
    """reads image as bytes string"""
    return np.asarray(Image.open("tests/api/fixtures/eight.png"))


class TestNumpyImageDecoders:
    """Tests the numpy decoder methods"""

    @staticmethod
    def test_image_to_numpy(image_bytes, image_array):
        """test csv data is correctly decoded to numpy array"""
        actual = numpy_image_decoders.image_to_numpy(image_bytes)

        np.testing.assert_equal(actual, image_array)
