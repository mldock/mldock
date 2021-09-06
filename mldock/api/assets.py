
import logging
from pathlib import Path

from pyarrow import fs
import gcsfs
import s3fs

from mldock.platform_helpers import utils

logger = logging.getLogger('mldock')
logger.setLevel(logging.INFO)

def infer_filesystem_type(path: str):
    """
        infers appropriate filesystem type and returns pyarrow support file-system

        args:
            path (str): full path/uri
        returns:
            file_system: a supported file-system type
            path: path without scheme
    """

    if utils._check_if_cloud_scheme(path, scheme=''):
        file_system = fs.LocalFileSystem()
    elif utils._check_if_cloud_scheme(path, scheme='s3'):
        path_without_scheme = utils.strip_scheme(path)
        file_system, path = s3fs.S3FileSystem(), path_without_scheme
    elif utils._check_if_cloud_scheme(path, scheme='gs'):
        path_without_scheme = utils.strip_scheme(path)
        file_system, path = gcsfs.GCSFileSystem(), path_without_scheme
    else:
        raise TypeError(
            "path scheme = '{SCHEME}' for '{PATH}' "
            "is not currently supported. "
            "Available options = 's3' or 'gs' "
            "or local filesystem path".format(
                SCHEME=utils.get_scheme(path),
                PATH=path
            )
        )
    return file_system, path

def upload_assets(fs_base_path, local_path, storage_location):
    """Uploads logs to specified file-system"""

    file_system, fs_base_path = infer_filesystem_type(fs_base_path)

    # create full artifacts base path
    artifacts_base_path = Path(
        fs_base_path,
        storage_location
    )

    local = fs.LocalFileSystem()

    file_selector = fs.FileSelector(
        local_path,
        recursive=True
    )
    for file in local.get_file_info(file_selector):
        src_path = Path(file.path)
        file_name = src_path.name
        dst_path = Path(artifacts_base_path, file_name)

        if isinstance(file_system, fs.LocalFileSystem):
            artifacts_base_path.mkdir(parents=True, exist_ok=True)
            file_system.copy_file(src_path.as_posix(), dst_path.as_posix())
        else:
            file_system.upload(src_path.as_posix(), dst_path.as_posix())
