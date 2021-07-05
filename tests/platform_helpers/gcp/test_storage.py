"""Test GS storage helpers"""
from pathlib import Path
import tempfile
from mock import patch
from mldock.platform_helpers.gcp import storage
from tests.mocks.google.storage import GSBucket, GSBucketObject

class TestGSStorage:
    """Test google storage helpers"""

    @staticmethod
    def setup_storage_mocks(bucket_name, filename, storage_destination, MockStorageClient):
        """
            setup up storage mocks for GS storage

            returns:
                (bucket: GSBucket, blob: GSBucketObject)
        """
        bucket = GSBucket(name=bucket_name, objects=[filename])
        blob = GSBucketObject(name=storage_destination, bucket=bucket)
        MockStorageClient().get_bucket.return_value = bucket
        return bucket, blob

    @patch('mldock.platform_helpers.gcp.storage.StorageClient')
    @patch('mldock.platform_helpers.gcp.storage.download_blob_to_filename')
    def test_download_blob_to_filename_recieved_correct_args(self, mock_download_blob_to_filename, MockStorageClient):
        """
            test that download_blob_to_filename recieves the correct arguments
            during download_folder.
        """
        bucket_name = 'some-bucket'
        prefix_path = 'some/prefix'
        filename = 'file.txt'
        local_path = 'tmp/local/path'

        storage_destination = Path(prefix_path, filename).as_posix()

        bucket, blob = self.setup_storage_mocks(
            bucket_name,
            filename,
            storage_destination,
            MockStorageClient
        )

        storage.download_folder(
            bucket_name=bucket_name,
            prefix=prefix_path,
            target=local_path
        )

        args, kwargs = mock_download_blob_to_filename.call_args

        assert args == (blob, prefix_path, filename, local_path), (
            "Failed. download_blob_to_filename recieved the wrong arguments"
        )

    @patch('mldock.platform_helpers.gcp.storage._iter_nested_dir')
    @patch('mldock.platform_helpers.gcp.storage.StorageClient')
    @patch('mldock.platform_helpers.gcp.storage.upload_blob_from_filename')
    def test_upload_blob_from_filename_recieved_correct_args(
        self,
        mock_upload_blob_from_filename,
        MockStorageClient,
        mock__iter_nested_dir
    ):
        """
            test that upload_blob_from_filename recieves the correct arguments
            during upload_folder.
        """
        bucket_name = 'some-bucket'
        prefix_path = 'some/prefix'
        filename = 'file.txt'

        storage_destination = Path(prefix_path, filename).as_posix()

        with tempfile.TemporaryDirectory() as tmp_dir:
            local_path = tmp_dir
            path = Path(local_path, filename)
            path.touch()

            bucket, _ = self.setup_storage_mocks(
                bucket_name,
                filename,
                storage_destination,
                MockStorageClient
            )
            mock__iter_nested_dir.return_value = [path]

            storage.upload_folder(
                local_path=local_path,
                bucket_name=bucket_name,
                prefix=prefix_path
            )
            args, kwargs = mock_upload_blob_from_filename.call_args

        assert args == (bucket, path, storage_destination), (
            "Failed. upload_blob_from_filename recieved the wrong arguments"
        )
