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
import itertools

from mock import Mock, patch
import numpy as np
import pytest
from six import BytesIO

from mldock.platform_helpers.mldock.inference.content_encoders import (
    numpy as numpy_encoders,
)


class TestNumpyEncoders:
    """Tests the numpy encoder methods"""

    @staticmethod
    @pytest.mark.parametrize(
        "target",
        [
            [42, 6, 9],
            [42.0, 6.0, 9.0],
            ["42", "6", "9"],
            ["42", "6", "9"],
            {42: {"6": 9.0}},
        ],
    )
    def test_array_to_npy(target):
        """test numpy arrays are correctly encoded as .npy"""
        input_data = np.array(target)

        actual = numpy_encoders.array_to_npy(input_data)

        np.testing.assert_equal(
            np.load(BytesIO(actual), allow_pickle=True), np.array(target)
        )

        actual = numpy_encoders.array_to_npy(target)

        np.testing.assert_equal(
            np.load(BytesIO(actual), allow_pickle=True), np.array(target)
        )

    @staticmethod
    @pytest.mark.parametrize(
        "target, expected",
        [
            ([42, 6, 9], "[42, 6, 9]"),
            ([42.0, 6.0, 9.0], "[42.0, 6.0, 9.0]"),
            (["42", "6", "9"], '["42", "6", "9"]'),
            ({42: {"6": 9.0}}, '{"42": {"6": 9.0}}'),
        ],
    )
    def test_array_to_json(target, expected):
        """test numpy arrays are correctly encoded as json"""
        actual = numpy_encoders.array_to_json(target)
        np.testing.assert_equal(actual, expected)

        actual = numpy_encoders.array_to_json(np.array(target))
        np.testing.assert_equal(actual, expected)

    @staticmethod
    @pytest.mark.parametrize(
        "target, expected, quoted",
        [
            ([42.0, 6.0, 9.0], "42.0\n6.0\n9.0\n", False),
            (["42", "6", "9"], "42\n6\n9\n", False),
            ([42, 6, 9], '"42"\n"6"\n"9"\n', True),
            ([42.0, 6.0, 9.0], '"42.0"\n"6.0"\n"9.0"\n', True),
            (["42", "6", "9"], '"42"\n"6"\n"9"\n', True),
            (["False,", "True.", "False,"], '"False,"\n"True."\n"False,"\n', True),
            (["aaa", 'b"bb', "ccc"], '"aaa"\n"b"bb"\n"ccc"\n', True),
            (["a\nb", "c"], '"a\nb"\n"c"\n', True),
        ],
    )
    def test_array_to_csv(target, expected, quoted):
        """test numpy arrays are correctly encoded as csv"""
        actual = numpy_encoders.array_to_csv(target, quoted=quoted)
        np.testing.assert_equal(actual, expected)

        actual = numpy_encoders.array_to_csv(
            np.array(target).astype(str), quoted=quoted
        )
        np.testing.assert_equal(actual, expected)
