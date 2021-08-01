"""LOGS GROK COMMANDS"""
import json
from pathlib import Path
import logging
import click
from clickclick import choice
from pygrok import Grok

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
    grok = Grok(pattern)

    log_dir = Path(log_path)

    log_runs = [log.parents[0].name for log in log_dir.glob('**/*') if log.name == log_file]

    state = choice('Select a run', log_runs, default=None)

    for log in log_dir.glob('**/*'):
        if log.parents[0].name == state:
            break

    with open(log.as_posix()) as file_:
        logs = file_.read()

    metadata = []
    for log in logs.split('\n'):

        result = grok.match(log)
        if result is not None:
            metadata.append(result)

    print(json.dumps(metadata, indent=4, sort_keys=True))

grok.add_command(parse)
