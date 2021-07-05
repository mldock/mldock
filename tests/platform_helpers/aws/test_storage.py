"""Test AWS s3 storage helpers"""
from pathlib import Path
import tempfile
from mock import patch
from mldock.platform_helpers.aws import storage
from tests.mocks.aws.boto3.s3 import AWSBucket, Objects, S3Resource, AWSBucketObject

class TestAWSStorage:
    """Test aws s3 storage helpers"""

    @staticmethod
    def setup_storage_mocks(bucket_name, prefix_path, filename, storage_destination, mock_boto3):
        """
            setup up storage mocks for S3 storage

            returns:
                (bucket: AWSBucket, blob: AWSBucketObject)
        """
        aws_bucket_objects = Objects(bucket_name=bucket_name, files=[filename])
        bucket = AWSBucket(name=bucket_name, objects=aws_bucket_objects)
        bucket_object = AWSBucketObject(
            key=Path(prefix_path, filename).as_posix(),
            bucket_name=bucket_name
        )
        s3_resource = S3Resource(resource='s3', bucket=bucket)

        mock_boto3.resource.return_value = s3_resource

        return bucket, bucket_object

    @patch('mldock.platform_helpers.aws.storage.boto3')
    @patch('mldock.platform_helpers.aws.storage.download_file_from_bucket')
    def test_download_file_from_bucket_recieved_correct_args(self, mock_download_file_from_bucket, mock_boto3):
        """
            test that download_file_from_bucket recieves the correct arguments
            during download_folder.
        """
        bucket_name = 'some-bucket'
        prefix_path = 'some/prefix'
        filename = 'file.txt'
        local_path = 'tmp/local/path'
        storage_destination = Path(prefix_path, 'file.txt').as_posix()

        bucket, bucket_object = self.setup_storage_mocks(
            bucket_name, prefix_path, filename, storage_destination, mock_boto3
        )

        storage.download_folder(
            bucket_name=bucket_name,
            prefix=prefix_path,
            target='tmp/local/path'
        )

        args, kwargs = mock_download_file_from_bucket.call_args
        print(args, kwargs)
        # maybe get args given?
        assert args ==(bucket, bucket_object, 'some/prefix', 'file.txt', 'tmp/local/path'), (
            "Failed. download_file_from_bucket recieved the wrong arguments"
        )

    @patch('mldock.platform_helpers.aws.storage._iter_nested_dir')
    @patch('mldock.platform_helpers.aws.storage.boto3')
    @patch('mldock.platform_helpers.aws.storage.upload_file_to_bucket')
    def test_upload_file_to_bucket_recieved_correct_args(self, mock_upload_file_to_bucket, mock_boto3, mock__iter_nested_dir):
        """
            test that upload_file_to_bucket recieves the correct arguments
            during upload_folder.
        """
        bucket_name = 'some-bucket'
        prefix_path = 'some/prefix'
        filename = 'file.txt'
        storage_destination = Path(prefix_path, 'file.txt').as_posix()

        with tempfile.TemporaryDirectory() as tmp_dir:
            local_path = tmp_dir
            path = Path(local_path, 'file.txt')
            path.touch()

            bucket, bucket_object = self.setup_storage_mocks(
                bucket_name, prefix_path, filename, storage_destination, mock_boto3
            )

            mock__iter_nested_dir.return_value = [path]

            storage.upload_folder(
                local_path=local_path,
                bucket_name=bucket_name,
                prefix=prefix_path
            )
            args, kwargs = mock_upload_file_to_bucket.call_args

        # maybe get args given?
        assert args == (bucket, path, storage_destination), (
            "Failed. upload_file_to_bucket recieved the wrong arguments"
        )
