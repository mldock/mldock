from pathlib import Path
from dataclasses import dataclass


@dataclass
class GSBucketObject:
    """Class for mocking the google storage bucket object blob."""

    name: str
    bucket: str

    @staticmethod
    def download_to_filename(local_path):
        print("download_to_filename: {}".format(local_path))

    @staticmethod
    def upload_from_filename(local_path):
        print("upload_to_filename: {}".format(local_path))


@dataclass
class GSBucket:
    """Class for mocking the google storage bucket object."""

    name: str
    objects: list

    def list_blobs(self, prefix) -> list:
        print("listing these blobs")
        return [
            GSBucketObject(bucket=self, name=Path(prefix, item).as_posix())
            for item in self.objects
        ]

    def blob(self, prefix):
        print("running this blob")
        return GSBucketObject(bucket=self, name=prefix)
