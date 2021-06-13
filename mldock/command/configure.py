import os
from pathlib import Path
import logging
import click

from mldock.config_managers.cli import \
    CliConfigureManager

click.disable_unicode_literals_warning = True
logger=logging.getLogger('mldock')

@click.group()
def configure():
    """
    Commands to configure mldock cli.
    """
    pass

@click.command()
@click.pass_obj
def local(obj):
    """Configure for local development tools"""
    
    config_manager = CliConfigureManager(type='local', create=True)
    config_manager.setup_config()
    config_manager.write_file()

    states = config_manager.get_state()

    for state in states:
        click.echo(click.style(state["name"], bg='blue'), nl=True)
        click.echo(click.style(state["message"], fg='white'), nl=True)

@click.command()
@click.pass_obj
def show(obj):
    """Configure for local development tools"""
    try:
        config_manager = CliConfigureManager()

        states = config_manager.get_state()

        for state in states:
            click.echo(click.style(state["name"], bg='blue'), nl=True)
            click.echo(click.style(state["message"], fg='white'), nl=True)
    except FileNotFoundError as exception:
        if Path(exception.filename).name == 'mldock':
            logger.error("File not found. Please run 'mldock configure local' to generate cli configuration.")
        else:
            raise

configure.add_command(local)
configure.add_command(show)
