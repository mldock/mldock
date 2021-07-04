"""Mock AWS Client and Resource"""
from dataclasses import dataclass

@dataclass
class AWSBucketObject:
    """Class for mocking the aws s3 storage bucket object blob."""
    key: str

    @staticmethod
    def download_file(prefix, local_path):
        print("download_to_filename: {} -> {}".format(prefix, local_path))

    @staticmethod
    def upload_file(local_path, remote_path):
        print("upload_to_filename: {} -> {}".format(local_path, remote_path))

@dataclass
class AWSBucket:
    """Class for mocking the aws s3 storage bucket object."""
    name: str
    class objects:
        def filter(self, Prefix) -> AWSBucketObject:
            print("listing these blobs")
            return [
                AWSBucketObject(key=Path(Prefix, item).as_posix())
                for item in self.objects
            ]
