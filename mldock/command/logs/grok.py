"""LOGS GROK COMMANDS"""
import json
from pathlib import Path
import logging
import click
from clickclick import choice

from mldock.api.logs import parse_grok, get_all_file_objects

click.disable_unicode_literals_warning = True
logger = logging.getLogger('mldock')
MLDOCK_CONFIG_NAME = 'mldock.json'


@click.group()
def grok():
    """
    Commands to manage and interact with logs using grok.
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
@click.option(
    '--pattern',
    type=str,
    help='a grok pattern'
)
def parse(log_path, log_file, pattern):
    """parse logs using a custom crok config and show"""
    
    logs = get_all_file_objects(log_path, log_file)

    log_runs = [Path(log.path).parents[0].name for log in logs]

    state = choice('Select a run', log_runs, default=None)

    for log in logs:
        if Path(log.path).parents[0].name == state:
            log_file_path = log.path
            break

    metadata = parse_grok(log_file_path, pattern)

    print(json.dumps(metadata, indent=4, sort_keys=True))

grok.add_command(parse)
