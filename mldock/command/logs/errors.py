"""LOGS ERRORS COMMANDS"""
import json
import logging
from pathlib import Path
import click
from clickclick import choice

from mldock.api.logs import parse_grok, get_all_file_objects, infer_filesystem_type

click.disable_unicode_literals_warning = True
logger = logging.getLogger('mldock')

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
@click.pass_obj
def show(obj, log_path, log_file):
    """show errors for all runs as a table"""

    pattern = 'Exception during %{WORD:script}\: %{GREEDYDATA:msg}'
    file_system, log_path = infer_filesystem_type(log_path)

    logs = get_all_file_objects(log_path, log_file, file_system)

    log_runs = [Path(log).parents[0].name for log in logs]

    state = choice('Select a run', log_runs, default=None)

    for log in logs:
        if Path(log).parents[0].name == state:
            log_file_path = log
            break

    metadata = parse_grok(log_file_path, pattern, file_system)

    reset_terminal()
    logger.info(obj['logo'])
    print(f"Script => {metadata['script']}")
    print(f"Exception:\n\n{metadata['msg']}")


errors.add_command(show)
