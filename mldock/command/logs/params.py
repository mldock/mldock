"""LOGS PARAMS COMMANDS"""
from pathlib import Path
import logging
import click
from clickclick.console import print_table
from mldock.api.logs import parse_grok_multiline, get_all_file_objects, infer_filesystem_type

click.disable_unicode_literals_warning = True
logger = logging.getLogger('mldock')
MLDOCK_CONFIG_NAME = 'mldock.json'
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

@click.group()
def params():
    """
    Commands to manage and interact with params logs.
    """

@click.command()
@click.option(
    '--log-path',
    type=str,
    help='a grok pattern'
)
@click.option(
    '--log-file',
    type=str,
    default='logs.txt',
    help='file name'
)
def show(log_path, log_file):
    """show params for all runs as a table"""

    pattern=r"param: %{WORD:name}=%{NUMBER:value};"

    file_system, log_path = infer_filesystem_type(log_path)

    logs = get_all_file_objects(log_path, log_file, file_system)

    keys = set()
    rows = list()
    for log in logs:
        run_id = Path(log).parents[0].name
        experiment = Path(log).parents[1].relative_to(log_path).as_posix().replace("/", ":")
        keys.add('run_id')
        keys.add('experiment')
        metadata = parse_grok_multiline(log, pattern, file_system)

        row = dict()
        row.update({'run_id': run_id})
        row.update({'experiment': experiment})
        for obj in metadata:
            keys.add(obj['name'])
            row.update(
                {obj['name']: obj['value']}
            )
        rows.append(row)

    print_table(keys, rows,
            styles=STYLES, titles=TITLES, max_column_widths=MAX_COLUMN_WIDTHS)

params.add_command(show)
