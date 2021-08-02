"""LOGS API UTILITIES"""
from pathlib import Path
from pygrok import Grok

from mldock.platform_helpers import utils
from pyarrow import fs
import gcsfs
import s3fs


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
        return fs.LocalFileSystem(), path
    elif utils._check_if_cloud_scheme(path, scheme='s3'):
        path_without_scheme = utils.strip_scheme(path)
        return s3fs.S3FileSystem(), path_without_scheme
    elif utils._check_if_cloud_scheme(path, scheme='gs'):
        path_without_scheme = utils.strip_scheme(path)
        return gcsfs.GCSFileSystem(), path_without_scheme
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

def parse_grok(file_path, pattern, file_system):
    """parse logs using a custom crok config and show"""
    grok = Grok(pattern)

    metadata = []

    if isinstance(file_system, fs.LocalFileSystem):
        with file_system.open_input_stream(file_path) as file_:
            log_data = file_.read().decode()
    else:
        with file_system.open(file_path, 'rb') as file_:
            log_data = file_.read().decode()

    for log in log_data.split('\n'):

        result = grok.match(log)
        if result is not None:
            metadata.append(result)

    return metadata

def get_all_file_objects(log_path, log_file):
    """parse logs using a custom crok config and show"""

    # log_dir = Path(log_path)
    file_system, log_path = infer_filesystem_type(log_path)

    file_selector = fs.FileSelector(log_path, recursive=True)
    logs = [log for log in file_system.get_file_info(file_selector) if log.base_name == log_file ]
            
    return logs

def get_all_file_objects_re(log_path, log_file, file_system):
    """parse logs using a custom crok config and show"""

    if isinstance(file_system, fs.LocalFileSystem):
        file_selector = fs.FileSelector(log_path, recursive=True)
        logs = [log.path for log in file_system.get_file_info(file_selector) if log.base_name == log_file ]
    else:
        logs = [log for log in file_system.glob(f'{log_path}/**') if Path(log).name == log_file ]
            
    return logs
