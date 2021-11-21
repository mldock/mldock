from pyarrow import fs
import gcsfs
import s3fs

from mldock.platform_helpers import utils


def infer_filesystem_type(path: str):
    """
    infers appropriate filesystem type and returns pyarrow support file-system

    args:
        path (str): full path/uri
    returns:
        file_system: a supported file-system type
        path: path without scheme
    """

    if utils.check_if_cloud_scheme(path, scheme=""):
        file_system = fs.LocalFileSystem()
    elif utils.check_if_cloud_scheme(path, scheme="s3"):
        path_without_scheme = utils.strip_scheme(path)
        file_system, path = s3fs.S3FileSystem(), path_without_scheme
    elif utils.check_if_cloud_scheme(path, scheme="gs"):
        path_without_scheme = utils.strip_scheme(path)
        file_system, path = gcsfs.GCSFileSystem(), path_without_scheme
    else:
        raise TypeError(
            "path scheme = '{SCHEME}' for '{PATH}' "
            "is not currently supported. "
            "Available options = 's3' or 'gs' "
            "or local filesystem path".format(SCHEME=utils.get_scheme(path), PATH=path)
        )
    return file_system, path
