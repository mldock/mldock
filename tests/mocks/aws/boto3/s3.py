"""Mock AWS Client and Resource"""
from pathlib import Path
from dataclasses import dataclass

@dataclass
class Objects:
    bucket_name: str
    files: list
    def filter(self, Prefix) -> list:
        print("listing these blobs")
        return [
            AWSBucketObject(key=Path(Prefix, item).as_posix(), bucket_name=self.bucket_name)
            for item in self.files
        ]
@dataclass
class AWSBucket:
    """Class for mocking the aws s3 storage bucket object."""
    name: str
    objects: Objects
    @staticmethod
    def download_file(prefix, local_path):
        print("download_to_filename: {} -> {}".format(prefix, local_path))
    @staticmethod
    def upload_file(local_path, remote_path):
        print("upload_to_filename: {} -> {}".format(local_path, remote_path))

@dataclass
class AWSBucketObject:
    """Class for mocking the aws s3 storage bucket object blob."""
    key: str
    bucket_name: AWSBucket

@dataclass
class S3Resource:
    resource: str
    bucket: AWSBucket

    def Bucket(self, bucket_name):
        del bucket_name
        return self.bucket
