"""Test GS storage helpers"""
from pathlib import Path
import tempfile
from mock import patch
from mldock.platform_helpers.gcp import storage
from tests.mocks.google.storage import Client as mock_storage_client
from dataclasses import dataclass

@dataclass
class GSBucketObjectBlob:
    """Class for mocking the google storage bucket object blob."""
    name: str
    bucket: str

    def download_to_filename(prefix):
        print(prefix)
    
    def upload_from_filename(prefix):
        print(prefix)

@dataclass
class GSBucketObject:
    """Class for mocking the google storage bucket object."""
    name: str
    def list_blobs(self) -> GSBucketObjectBlob:
        return [
            GSBucketObjectBlob(bucket=self.name, name='path/to/my/file')
        ]
    def blob(self, prefix):
        return GSBucketObjectBlob(bucket=self.name, name=prefix)

class TestGSStorage:
    @patch('storage.Client')
    def test_download_folder_successful(StorageClient):
        """
            - test that it get's the correct arguments eventually in download_from_filename accordind to what is passed.
            - test that each API get's the correct thing
        """
        storage_client = StorageClient()
        storage_client.get_bucket.return_value = GSBucketObject(name='myfake-bucket')

        storage.download_folder(
            bucket_name='some-bucket',
            prefix='some/prefix',
            target='tmp/local/path'
        )

