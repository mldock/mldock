from pathlib import Path
from dataclasses import dataclass

@dataclass
class GSBucketObjectBlob:
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
class GSBucketObject:
    """Class for mocking the google storage bucket object."""
    name: str
    objects: list

    def list_blobs(self, prefix) -> GSBucketObjectBlob:
        print("listing these blobs")
        return [
            GSBucketObjectBlob(bucket=self, name=Path(prefix, item).as_posix())
            for item in self.objects
        ]

    def blob(self, prefix):
        print("running this blob")
        return GSBucketObjectBlob(bucket=self, name=prefix)


