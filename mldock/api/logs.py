"""LOGS API UTILITIES"""
import logging
from pathlib import Path
from clickclick.console import print_table
from pygrok import Grok
from pyarrow import fs

from mldock.api.assets import infer_filesystem_type

logger = logging.getLogger('mldock')

STYLES = {
    'FINE': {'fg': 'green'},
    'ERROR': {'fg': 'red'},
    'WARNING': {'fg': 'yellow', 'bold': True},
}


TITLES = {
    'state': 'Status',
    'creation_time': 'Creation Date',
    'id': 'Identifier',
    'desc': 'Description',
    'name': 'Name',
}

MAX_COLUMN_WIDTHS = {
    'desc': 50,
    'name': 20,
}

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

    log_data = read_file_stream(file_path, file_system)

    metadata = grok.match(log_data.replace('\n', '\\n'))

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
        logs = [
            log.path
            for log in file_system.get_file_info(file_selector)
            if log.base_name == file_name
        ]
    else:
        logs = [
            log
            for log in file_system.glob(f'{base_path}/**')
            if Path(log).name == file_name
        ]

    return logs

def extract_records_with_pattern(pattern, log_path, log_file):

    file_system, log_path = infer_filesystem_type(log_path)

    logs = get_all_file_objects(log_path, log_file, file_system)

    keys = set()
    rows = []
    for log in logs:
        run_id = Path(log).parents[0].name
        experiment = Path(log).parents[1].relative_to(log_path).as_posix().replace("/", ":")
        keys.add('run_id')
        keys.add('experiment')
        metadata = parse_grok_multiline(log, pattern, file_system)

        row = {}
        row.update({'run_id': run_id})
        row.update({'experiment': experiment})
        for obj in metadata:
            keys.add(obj['name'])
            row.update(
                {obj['name']: obj['value']}
            )
        rows.append(row)

    logger.info(metadata)
    print_table(keys, rows,
            styles=STYLES, titles=TITLES, max_column_widths=MAX_COLUMN_WIDTHS)
