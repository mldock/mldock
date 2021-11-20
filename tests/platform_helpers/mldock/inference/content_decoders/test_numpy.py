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

from mldock.platform_helpers.mldock.inference.content_decoders import (
    numpy as numpy_decoders,
)


@pytest.fixture
def image_bytes():
    """reads image as bytes string"""
    with open("tests/api/fixtures/eight.png", "rb") as file_:
        return io.BytesIO(file_.read())


@pytest.fixture
def image_array():
    """reads image as bytes string"""
    return np.asarray(Image.open("tests/api/fixtures/eight.png"))


class TestNumpyDecoders:
    """Tests the numpy decoder methods"""

    def test_csv_to_numpy(image_bytes, image_array):
        """test csv data is correctly decoded to numpy array"""
        actual = numpy_decoders.image_to_numpy(image_bytes)

        np.testing.assert_equal(actual, image_array)

    @staticmethod
    @pytest.mark.parametrize(
        "target",
        (
            [42, 6, 9],
            [42.0, 6.0, 9.0],
            ["42", "6", "9"],
            [u"42", u"6", u"9"],
            {42: {"6": 9.0}},
        ),
    )
    def test_npy_to_numpy(target):
        buffer = io.BytesIO()
        np.save(buffer, target)
        input_data = buffer.getvalue()

        actual = numpy_decoders.npy_to_numpy(input_data)

        np.testing.assert_equal(actual, np.array(target))

    @staticmethod
    @pytest.mark.parametrize(
        "target, expected",
        [
            ("[42, 6, 9]", np.array([42, 6, 9])),
            ("[42.0, 6.0, 9.0]", np.array([42.0, 6.0, 9.0])),
            ('["42", "6", "9"]', np.array(["42", "6", "9"])),
            (u'["42", "6", "9"]', np.array([u"42", u"6", u"9"])),
        ],
    )
    def test_json_to_numpy(target, expected):
        """test json data is correctly decoded to numpy array"""
        actual = numpy_decoders.json_to_numpy(target)
        np.testing.assert_equal(actual, expected)

    @staticmethod
    @pytest.mark.parametrize(
        "target, expected",
        [
            (b"42\n6\n9\n", np.array([42, 6, 9]).astype(str)),
            (b"42.0\n6.0\n9.0\n", np.array([42.0, 6.0, 9.0]).astype(str)),
            (b"42\n6\n9\n", np.array([42, 6, 9]).astype(str)),
            (b'"False,"\n"True."\n"False,"\n', np.array(["False,", "True.", "False,"])),
            (b'aaa\n"b""bb"\nccc\n', np.array(["aaa", 'b"bb', "ccc"])),
            (b'"a\nb"\nc\n', np.array(["a\nb", "c"])),
        ],
    )
    def test_csv_to_numpy(target, expected):
        """test csv data is correctly decoded to numpy array"""
        actual = numpy_decoders.csv_to_numpy(target)

        np.testing.assert_equal(actual, expected)
