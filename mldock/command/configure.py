"""CONFIGURE CLI COMMANDS"""
from pathlib import Path
import logging
import click

from mldock.config_managers.cli import \
    CliConfigureManager

click.disable_unicode_literals_warning = True
logger=logging.getLogger('mldock')

def reset_terminal():
    """clears the terminal view frame"""
    click.clear()

@click.group()
def configure():
    """
    Commands to configure mldock cli.
    """

@click.command()
def init():
    """Configure  development tools"""
    config_manager = CliConfigureManager(create=True)
    config_manager.write_file()

@click.command()
@click.option(
    '-c', '--config-name',
    help='Configuration name you wish to reset',
    required=True,
    type=click.Choice(
        ['local', 'workspace', 'templates', 'all'],
        case_sensitive=False
    )
)
@click.pass_obj
def reset(obj, config_name):
    """reset configurations"""
    config_manager = CliConfigureManager()
    if config_name == 'all':
        for config in ['local', 'workspace', 'templates']:
            config_manager.reset(config)
    else:
        config_manager.reset(config_name)
    config_manager.write_file()

    reset_terminal()
    logger.info(obj['logo'])
    states = config_manager.get_state()

    for state in states:
        click.echo(click.style(state["name"], bg='blue'), nl=True)
        click.echo(click.style(state["message"], fg='white'), nl=True)

@click.command()
@click.pass_obj
def workspace(obj):
    """Configure for local development tools"""

    config_manager = CliConfigureManager(create=True)
    config_manager.setup_workspace_config()
    config_manager.write_file()

    reset_terminal()
    logger.info(obj['logo'])
    states = config_manager.get_state()

    for state in states:
        click.echo(click.style(state["name"], bg='blue'), nl=True)
        click.echo(click.style(state["message"], fg='white'), nl=True)

@click.command()
@click.pass_obj
def local(obj):
    """Configure for local development tools"""

    config_manager = CliConfigureManager(create=True)
    config_manager.setup_local_config()
    config_manager.write_file()

    reset_terminal()
    logger.info(obj['logo'])
    states = config_manager.get_state()

    for state in states:
        click.echo(click.style(state["name"], bg='blue'), nl=True)
        click.echo(click.style(state["message"], fg='white'), nl=True)

@click.command()
@click.pass_obj
def templates(obj):
    """Configure for local development tools"""

    config_manager = CliConfigureManager(create=True)
    config_manager.setup_templates_config()
    config_manager.write_file()

    reset_terminal()
    logger.info(obj['logo'])
    states = config_manager.get_state()

    for state in states:
        click.echo(click.style(state["name"], bg='blue'), nl=True)
        click.echo(click.style(state["message"], fg='white'), nl=True)

@click.command()
def show():
    """Configure for local development tools"""
    try:
        config_manager = CliConfigureManager()

        states = config_manager.get_state()

        for state in states:
            click.echo(click.style(state["name"], bg='blue'), nl=True)
            click.echo(click.style(state["message"], fg='white'), nl=True)
    except FileNotFoundError as exception:
        if Path(exception.filename).name == 'mldock':
            logger.error(
                "File not found. Please run 'mldock configure local' "
                "to generate cli configuration."
            )
        else:
            raise

def add_commands(cli_group: click.group):
    """
        add commands to cli group
        args:
            cli (click.group)
    """
    cli_group.add_command(init)
    cli_group.add_command(workspace)
    cli_group.add_command(local)
    cli_group.add_command(templates)
    cli_group.add_command(show)
    cli_group.add_command(reset)

add_commands(configure)
