"""Test logs API utilities"""
import pytest
from pyarrow import fs
import gcsfs
import s3fs
from mldock.api.assets import infer_filesystem_type

class TestAssetsAPI:
    """Test logs API utilities"""

    # Tests
    @staticmethod
    def test_infer_filesystem_type_success_return_localfilesystem():
        """test infer filesystem successful on local scheme"""
        file_system, path = infer_filesystem_type("/fake/file/path")

        assert file_system == fs.LocalFileSystem(), "Failure: expected local filesystem"

    @staticmethod
    def test_infer_filesystem_type_success_return_s3filesystem():
        """test infer filesystem successful on s3 scheme"""
        file_system, path = infer_filesystem_type("s3://fake/file/path")
        assert file_system == s3fs.S3FileSystem(), "Failure: expected s3 filesystem"

    @staticmethod
    def testinfer_filesystem_type_success_return_gcsfilesystem():
        """test infer filesystem successful on gcs scheme"""
        file_system, path = infer_filesystem_type("gs://fake/file/path")
        assert file_system == gcsfs.GCSFileSystem(), "Failure: expected gcs filesystem"

    @staticmethod
    def test_infer_filesystem_type_fail_unknown_scheme():
        """test infer filesystem fails on unkown scheme"""
        with pytest.raises(
            TypeError,
            match=(
                r"path scheme = 'fake' for 'fake://fake/file/path' "
                r"is not currently supported. "
                r"Available options = 's3' or 'gs' "
                r"or local filesystem path"
            )
        ):
            _ = infer_filesystem_type("fake://fake/file/path")
