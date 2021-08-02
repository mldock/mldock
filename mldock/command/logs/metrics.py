"""LOGS METRICS COMMANDS"""
import json
from pathlib import Path
import logging
import click
from clickclick.console import print_table
from mldock.api.logs import parse_grok, get_all_file_objects

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
def metrics():
    """
    Commands to manage and interact with metric logs.
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
    """show metrics for all runs as a table"""

    pattern="metric: %{WORD:name}=%{NUMBER:value};"

    logs = get_all_file_objects(log_path, log_file)

    keys = set()
    rows = list()
    for log in logs:
        run_id = Path(log.path).parents[0].name
        keys.add('run_id')
        metadata = parse_grok(log.path, pattern)

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

@click.command()
def diff():
    """show metrics for all runs as a table"""

def add_commands(cli_group: click.group):
    """
        add commands to cli group
        args:
            cli (click.group)
    """
    cli_group.add_command(show)
    cli_group.add_command(diff)

add_commands(metrics)
