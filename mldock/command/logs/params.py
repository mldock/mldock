"""LOGS PARAMS COMMANDS"""
import json
from pathlib import Path
import logging
import click
from clickclick.console import print_table

from pygrok import Grok

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

    pattern="param: %{WORD:name}=%{NUMBER:value};"
    grok = Grok(pattern)

    log_dir = Path(log_path)

    logs = [log for log in log_dir.glob('**/*') if log.name == log_file]

    keys = set()
    rows = list()
    for log in logs:
        run_id = log.parents[0].name
        keys.add('run_id')
        metadata = []
        with open(log.as_posix()) as file_:
            logs = file_.read()
        for log in logs.split('\n'):

            result = grok.match(log)
            if result is not None:
                metadata.append(result)

        row = dict()
        row.update({'run_id': run_id})
        for m in metadata:
            keys.add(m['name'])
            row.update(
                {m['name']: m['value']}
            )
        rows.append(row)

    print_table(keys, rows,
            styles=STYLES, titles=TITLES, max_column_widths=MAX_COLUMN_WIDTHS)

params.add_command(show)
