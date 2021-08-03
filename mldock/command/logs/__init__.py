"""LOGS COMMANDS"""
import logging
from pathlib import Path
import click
from clickclick import choice

from mldock.command.logs.metrics import metrics
from mldock.command.logs.params import params
from mldock.command.logs.grok import grok
from mldock.command.logs.errors import errors
from mldock.api.logs import read_file_stream, get_all_file_objects, infer_filesystem_type

click.disable_unicode_literals_warning = True
logger = logging.getLogger('mldock')
MLDOCK_CONFIG_NAME = 'mldock.json'

def reset_terminal():
    """clears the terminal view frame"""
    click.clear()

@click.group()
def logs():
    """
    Commands to manage and interact with logs.
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


    file_system, log_path = infer_filesystem_type(log_path)

    logs = get_all_file_objects(log_path, log_file, file_system)

    log_runs = [Path(log).parents[0].name for log in logs]

    state = choice('Select a run', log_runs, default=None)

    for log in logs:
        if Path(log).parents[0].name == state:
            log_file_path = log
            break

    log_data = read_file_stream(log_file_path, file_system)

    reset_terminal()
    print(log_data)

def add_commands(cli_group: click.group):
    """
        add commands to cli group
        args:
            cli (click.group)
    """
    cli_group.add_command(show)    
    cli_group.add_command(metrics)
    cli_group.add_command(params)
    cli_group.add_command(grok)
    cli_group.add_command(errors)

add_commands(logs)

