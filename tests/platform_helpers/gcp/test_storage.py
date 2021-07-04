"""Test GS storage helpers"""
from pathlib import Path
import tempfile
from mock import patch
from mldock.platform_helpers.gcp import storage
from tests.mocks.google.storage import GSBucketObject, GSBucketObjectBlob

class TestGSStorage:
    """Test google storage helpers"""
    @staticmethod
    @patch('mldock.platform_helpers.gcp.storage.StorageClient')
    @patch('mldock.platform_helpers.gcp.storage.download_blob_to_filename')
    def test_download_blob_to_filename_recieved_correct_args(mock_download_blob_to_filename, MockStorageClient):
        """
            - test that it get's the correct arguments eventually in download_from_filename accordind to what is passed.
            - test that each API get's the correct thing
        """
        bucket_name = 'some-bucket'
        prefix_path = 'some/prefix'
        storage_destination = Path(prefix_path, 'file.txt').as_posix()
        bucket = GSBucketObject(name=bucket_name, objects=['file.txt'])
        blob = GSBucketObjectBlob(name=storage_destination, bucket=bucket)
        MockStorageClient().get_bucket.return_value = bucket

        storage.download_folder(
            bucket_name=bucket_name,
            prefix=prefix_path,
            target='tmp/local/path'
        )

        args, kwargs = mock_download_blob_to_filename.call_args

        # maybe get args given?
        assert args == (blob, prefix_path, 'file.txt', 'tmp/local/path'), (
            "Failed. download_blob_to_filename recieved the wrong arguments"
        )

    @staticmethod
    @patch('mldock.platform_helpers.gcp.storage._iter_nested_dir')
    @patch('mldock.platform_helpers.gcp.storage.StorageClient')
    @patch('mldock.platform_helpers.gcp.storage.upload_blob_from_filename')
    def test_upload_blob_from_filename_recieved_correct_args(mock_upload_blob_from_filename, MockStorageClient, mock__iter_nested_dir):
        """
            - test that it get's the correct arguments eventually in download_from_filename accordind to what is passed.
            - test that each API get's the correct thing
        """
        bucket_name = 'some-bucket'
        prefix_path = 'some/prefix'
        storage_destination = Path(prefix_path, 'file.txt').as_posix()

        with tempfile.TemporaryDirectory() as tmp_dir:
            local_path = tmp_dir
            path = Path(local_path, 'file.txt')
            path.touch()

            bucket = GSBucketObject(name=bucket_name, objects=['file.txt'])
            MockStorageClient().get_bucket.return_value = bucket
            mock__iter_nested_dir.return_value = [path]

            storage.upload_folder(
                local_path=local_path,
                bucket_name=bucket_name,
                prefix=prefix_path
            )
            args, kwargs = mock_upload_blob_from_filename.call_args

        # maybe get args given?
        assert args == (bucket, path, storage_destination), (
            "Failed. upload_blob_from_filename recieved the wrong arguments"
        )