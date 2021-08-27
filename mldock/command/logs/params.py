"""LOGS PARAMS COMMANDS"""
import logging
import click
from mldock.api.logs import extract_records_with_pattern

click.disable_unicode_literals_warning = True
logger = logging.getLogger('mldock')
MLDOCK_CONFIG_NAME = 'mldock.json'


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

    pattern=r"param: %{GREEDYDATA:name}=%{NUMBER:value};"

    extract_records_with_pattern(pattern, log_path, log_file)

params.add_command(show)
