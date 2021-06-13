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
import json

from mock import Mock, patch
# import numpy as np
import pandas as pd
import pytest
from scipy import sparse
from six import BytesIO

from mldock.platform_helpers.mldock.inference import content_types
from mldock.platform_helpers.mldock.inference.content_decoders import pandas as pandas_decoders


class TestPandasDecoders:
    """Tests the pandas decoder methods"""
    @pytest.mark.parametrize(
        "target, expected, dtype",
        [
            ({"col":[42, 6, 9]}, pd.DataFrame([42, 6, 9], columns=["col"]), int),
            ({"col":[42.0, 6.0, 9.0]}, pd.DataFrame([42.0, 6.0, 9.0], columns=["col"]), float),
            ({"col":["42", "6", "9"]}, pd.DataFrame(["42", "6", "9"], columns=["col"]), None),
            ({"col":[u"42", u"6", u"9"]}, pd.DataFrame([u"42", u"6", u"9"], columns=["col"]), None),
        ],
    )
    @staticmethod
    def test_json_list_to_pandas(target, expected, dtype):
        """test json data is correctly decoded to pandas dataframe"""
        actual = pandas_decoders.json_list_to_pandas(json.dumps(target), dtype=dtype)
        pd.testing.assert_frame_equal(actual, expected.astype(dtype))

    @pytest.mark.parametrize(
        "target, expected, dtype",
        [
            (b"col\n42\n6\n9\n", pd.DataFrame([42, 6, 9], columns=['col']), int),
            (b"col\n42.0\n6.0\n9.0\n", pd.DataFrame([42.0, 6.0, 9.0], columns=['col']), float),
            (b"col\n42\n6\n9\n", pd.DataFrame([42, 6, 9], columns=['col']), int),
            (b'col\n"False,"\n"True."\n"False,"\n', pd.DataFrame(["False,", "True.", "False,"], columns=['col']), str),
            (b'col\naaa\n"b""bb"\nccc\n', pd.DataFrame(["aaa", 'b"bb', "ccc"], columns=['col']), str),
            (b'col\n"a\nb"\nc\n', pd.DataFrame(["a\nb", "c"], columns=['col']), str)
        ],
    )
    @staticmethod
    def test_csv_to_pandas(target, expected, dtype):
        """test csv data is correctly decoded to pandas dataframe"""
        actual = pandas_decoders.csv_to_pandas(target, dtype=dtype)
        print(actual)
        pd.testing.assert_frame_equal(actual, expected)


    @pytest.mark.parametrize(
        "payload, content_type",
        [
            (42, content_types.JSON),
            (42, content_types.CSV)
        ],
    )
    @staticmethod
    def test_decode(payload, content_type):
        """test pandas decode method that decodes from a set of content-types"""
        decoder = Mock()
        with patch.dict(pandas_decoders._decoders_map, {content_type: decoder}, clear=True):
            pandas_decoders.decode(payload, content_type)

            decoder.assert_called_once_with(42)
