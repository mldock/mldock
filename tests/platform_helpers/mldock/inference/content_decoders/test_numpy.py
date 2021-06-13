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
from scipy import sparse
from six import BytesIO

from mldock.platform_helpers.mldock.inference import content_types
from mldock.platform_helpers.mldock.inference.content_decoders import numpy as numpy_decoders
from mldock.platform_helpers.mldock.inference.record_pb2 import Record
from mldock.platform_helpers.mldock.inference.recordio import _read_recordio


class TestNumpyDecoders:
    """Tests the numpy decoder methods"""

    @pytest.mark.parametrize(
        "target",
        ([42, 6, 9], [42.0, 6.0, 9.0], ["42", "6", "9"], [u"42", u"6", u"9"], {42: {"6": 9.0}}),
    )
    @staticmethod
    def test_npy_to_numpy(target):
        buffer = BytesIO()
        np.save(buffer, target)
        input_data = buffer.getvalue()

        actual = numpy_decoders.npy_to_numpy(input_data)

        np.testing.assert_equal(actual, np.array(target))


    @pytest.mark.parametrize(
        "target, expected, dtype",
        [
            ("[42, 6, 9]", np.array([42, 6, 9]), int),
            ("[42.0, 6.0, 9.0]", np.array([42.0, 6.0, 9.0]), float),
            ('["42", "6", "9"]', np.array(["42", "6", "9"]), None),
            (u'["42", "6", "9"]', np.array([u"42", u"6", u"9"]), None),
        ],
    )
    @staticmethod
    def test_json_to_numpy(target, expected, dtype):
        """test json data is correctly decoded to numpy array"""
        actual = numpy_decoders.json_to_numpy(target, dtype=dtype)
        np.testing.assert_equal(actual, expected)

        np.testing.assert_equal(numpy_decoders.json_to_numpy(target, dtype=int), expected.astype(int))

        np.testing.assert_equal(numpy_decoders.json_to_numpy(target, dtype=float), expected.astype(float))

    @pytest.mark.parametrize(
        "target, expected, dtype",
        [
            (b"42\n6\n9\n", np.array([42, 6, 9]), int),
            (b"42.0\n6.0\n9.0\n", np.array([42.0, 6.0, 9.0]), float),
            (b"42\n6\n9\n", np.array([42, 6, 9]), int),
            (b'"False,"\n"True."\n"False,"\n', np.array(["False,", "True.", "False,"]), None),
            (b'aaa\n"b""bb"\nccc\n', np.array(["aaa", 'b"bb', "ccc"]), None),
            (b'"a\nb"\nc\n', np.array(["a\nb", "c"]), None),
        ],
    )
    @staticmethod
    def test_csv_to_numpy(target, expected, dtype):
        """test csv data is correctly decoded to numpy array"""
        actual = numpy_decoders.csv_to_numpy(target, dtype=dtype)
        print(actual)
        np.testing.assert_equal(actual, expected)


    @pytest.mark.parametrize(
        "payload, content_type",
        [
            (42, content_types.JSON),
            (42, content_types.CSV),
            (42, content_types.NPY)
        ],
    )
    @staticmethod
    def test_decode(payload, content_type):
        """test numpy decode that decodes from a set of content-types"""
        decoder = Mock()
        with patch.dict(numpy_decoders._decoders_map, {content_type: decoder}, clear=True):
            numpy_decoders.decode(payload, content_type)

            decoder.assert_called_once_with(42)

