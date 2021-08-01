"""LOGS ERRORS COMMANDS"""
import logging
from pathlib import Path
import click
from clickclick import choice
from pygrok import Grok
click.disable_unicode_literals_warning = True
logger = logging.getLogger('mldock')
MLDOCK_CONFIG_NAME = 'mldock.json'

def reset_terminal():
    """clears the terminal view frame"""
    click.clear()

@click.group()
def errors():
    """
    Commands to manage and interact with errors logs.
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
    """show errors for all runs as a table"""


    log_dir = Path(log_path)

    log_runs = [log.parents[0].name for log in log_dir.glob('**/*') if log.name == log_file]

    state = choice('Select a run', log_runs, default=None)

    for log in log_dir.glob('**/*'):
        if log.parents[0].name == state:
            break

    with open(log.as_posix()) as file_:
        logs = file_.read()

    reset_terminal()
    print(logs)


errors.add_command(show)
