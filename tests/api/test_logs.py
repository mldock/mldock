"""Test logs API utilities"""
import tempfile
from pathlib import Path
import pytest
from mock import patch
from pyarrow import fs
from mldock.api.logs import (
    read_file_stream,
    parse_grok,
    get_all_file_objects,
    parse_grok_multiline,
)


class TestLogsAPI:
    """Test logs API utilities"""

    # Fixtures and setup
    @staticmethod
    def __create_textfile(my_path):
        """creates textfile and seeds it with msg"""
        # This currently assumes the path to the file exists.
        msg = "test that this works"
        with open(my_path, "w+") as file:
            file.write(msg)
        return msg

    # Tests
    def test_read_file_stream_success(self):
        """test reading file as stream returns correct msg"""
        tmp_dir = tempfile.TemporaryDirectory()

        txtfile = Path(tmp_dir.name, "logs.txt").as_posix()
        msg = self.__create_textfile(txtfile)

        file_system = fs.LocalFileSystem()

        txt_data = read_file_stream(txtfile, file_system)

        assert txt_data == msg, "Failure: file read did not match expected."

    @patch("mldock.api.logs.read_file_stream")
    def test_parse_grok_success_on_metrics_grok(self, mock_read_file_stream):
        """Test parse grok on single metric logs is success"""
        mock_read_file_stream.return_value = "metric: mae=4;\n"
        metadata = parse_grok(
            file_path="some/path",
            pattern="metric: %{WORD:name}=%{NUMBER:value};",
            file_system=fs.LocalFileSystem(),
        )

        assert metadata == {
            "name": "mae",
            "value": "4",
        }, "Failure. grok result was not correct according to pattern."

    @patch("mldock.api.logs.read_file_stream")
    def test_parse_grok_success_on_exception_grok(self, mock_read_file_stream):
        """Test parse grok on single Exception logs is success"""
        mock_read_file_stream.return_value = (
            "Exception during testscript: not a supported "
            "type.\nTypeError: not supported type"
        )
        metadata = parse_grok(
            file_path="some/path",
            pattern="Exception during %{WORD:script}\: %{GREEDYDATA:msg}",
            file_system=fs.LocalFileSystem(),
        )

        assert metadata == {
            "msg": "not a supported type.\\nTypeError: not supported type",
            "script": "testscript",
        }, "Failure. grok result was not correct according to pattern."

    @patch("mldock.api.logs.read_file_stream")
    def test_parse_grok_multiline_success_on_metrics_grok(self, mock_read_file_stream):
        """Test parse grok on multiline metric logs is success"""
        mock_read_file_stream.return_value = "metric: mae=4;\nmetric: acc=0.9;"
        metadata = parse_grok_multiline(
            file_path="some/path",
            pattern="metric: %{WORD:name}=%{NUMBER:value};",
            file_system=fs.LocalFileSystem(),
        )

        assert metadata == [
            {"name": "mae", "value": "4"},
            {"name": "acc", "value": "0.9"},
        ], "Failure. grok result was not correct according to pattern."

    def test_get_all_file_objects_success_local_filesystem(self):
        """Test get all file objects at base_path on local filesysystem is success"""
        tmp_dir = tempfile.TemporaryDirectory()

        txtfile = Path(tmp_dir.name, "logs.txt").as_posix()
        _ = self.__create_textfile(txtfile)

        files = get_all_file_objects(
            base_path=tmp_dir.name,
            file_name="logs.txt",
            file_system=fs.LocalFileSystem(),
        )

        print(files)
        assert files == [txtfile], "Failure. File objects did not match expected"
