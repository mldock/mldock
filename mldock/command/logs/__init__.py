"""LOGS COMMANDS"""
import logging
from pathlib import Path
import click

from mldock.command.logs.metrics import metrics
from mldock.command.logs.params import params
from mldock.command.logs.grok import grok
from mldock.command.logs.errors import errors

click.disable_unicode_literals_warning = True
logger = logging.getLogger('mldock')
MLDOCK_CONFIG_NAME = 'mldock.json'


@click.group()
def logs():
    """
    Commands to manage and interact with logs.
    """


def add_commands(cli_group: click.group):
    """
        add commands to cli group
        args:
            cli (click.group)
    """
    cli_group.add_command(metrics)
    cli_group.add_command(params)
    cli_group.add_command(grok)
    cli_group.add_command(errors)

add_commands(logs)

