"""LOGS API UTILITIES"""
from pathlib import Path
from pygrok import Grok
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

def read_file_stream(file_path, file_system):
    """
        Read file from file_system as a stream.

        args:
            file_path (str): path to file
            file_system (pyarrow.fs.FileSystem): pyarrow supported filesystem object
        return
            log_data (str): log data
    """
    if isinstance(file_system, fs.LocalFileSystem):
        with file_system.open_input_stream(file_path) as file_:
            log_data = file_.read().decode()
    else:
        with file_system.open(file_path, 'rb') as file_:
            log_data = file_.read().decode()
    return log_data

def parse_grok(file_path, pattern, file_system):
    """
        Parse logs using a custom crok pattern and return parsed objects.

        args:
            file_path (str): file path to object in file_system
            pattern (str): supported grok pattern
            file_system (pyarrow.fs.FileSystem): pyarrow supported file system object
        return:
            metadata (list): list of file objects as per grok pattern
    """
    grok = Grok(pattern)

    metadata = []

    log_data = read_file_stream(file_path, file_system)

    metadata = grok.match(log_data.replace('\n', '\\n'))

    metadata['msg'] = metadata['msg'].replace("\\n", "\n")
    return metadata

def parse_grok_multiline(file_path, pattern, file_system):
    """
        Parse logs using a custom crok pattern and return parsed objects.

        args:
            file_path (str): file path to object in file_system
            pattern (str): supported grok pattern
            file_system (pyarrow.fs.FileSystem): pyarrow supported file system object
        return:
            metadata (list): list of file objects as per grok pattern
    """
    grok = Grok(pattern)

    metadata = []

    log_data = read_file_stream(file_path, file_system)

    for log in log_data.split('\n'):

        result = grok.match(log)
        if result is not None:
            metadata.append(result)

    return metadata

def get_all_file_objects(base_path, file_name, file_system):
    """
        Get all file objects, filter and return all files matching file_name

        args:
            base_path (str): base path to start walk from to find file objects
            file_name (str): file names to match and return
            file_system (pyarrow.fs.FileSystem): pyarrow supported file system object
        return:
            file_paths (list): list of file paths
    """

    if isinstance(file_system, fs.LocalFileSystem):
        file_selector = fs.FileSelector(base_path, recursive=True)
        logs = [log.path for log in file_system.get_file_info(file_selector) if log.base_name == file_name ]
    else:
        logs = [log for log in file_system.glob(f'{base_path}/**') if Path(log).name == file_name ]
            
    return logs
