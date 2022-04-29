import gcsfs
from mldock.platform_helpers.mldock.asset_managers.base import BaseEnvArtifactManager
from mldock.platform_helpers.mldock.storage.pyarrow import (
    download_assets,
    upload_assets,
)


class GCSEnvArtifactManager(BaseEnvArtifactManager):
    """
    Extends the Environment class to give us
    more specific environment configuration tasks based on
    the GCP resource eco-system.
    """

    @staticmethod
    def download_assets(fs_base_path, local_path, storage_location):
        file_system = gcsfs.GCSFileSystem()
        download_assets(
            file_system,
            fs_base_path=fs_base_path,
            local_path=local_path,
            storage_location=storage_location,
        )

    @staticmethod
    def upload_assets(fs_base_path, local_path, storage_location):
        file_system = gcsfs.GCSFileSystem()
        upload_assets(
            file_system,
            fs_base_path=fs_base_path,
            local_path=local_path,
            storage_location=storage_location,
        )
