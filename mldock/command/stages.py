"""CONTAINER PROJECT MANAGEMENT COMMANDS"""
import os
import json
from pathlib import Path
import logging
import click

from mldock.config_managers.core import WorkingDirectoryManager
from mldock.config_managers.project import MLDockConfigManager
from mldock.config_managers.cli import (
    StageConfigManager,
    CliConfigureManager,
    RoutinesConfigManager
)

click.disable_unicode_literals_warning = True
logger = logging.getLogger("mldock")
MLDOCK_CONFIG_NAME = "mldock.yaml"

def reset_terminal():
    """clears the terminal view frame"""
    click.clear()


@click.group()
def stages():
    """
    Commands to create, update and manage projects and templates.
    """

@click.command()
@click.option(
    "--project_directory",
    "--dir",
    "-d",
    help="path to mldock project.",
    required=True,
    type=click.Path(
        exists=False,
        file_okay=False,
        dir_okay=True,
        writable=True,
        readable=True,
        resolve_path=False,
        allow_dash=False,
        path_type=None,
    ),
)
@click.pass_obj
def manage(obj, project_directory):
    """
    Command to update a given mldock project.
    """
    reset_terminal()
    try:
        logger.info("Loading MLDock config")
        mldock_manager = MLDockConfigManager(
            filepath=os.path.join(project_directory, MLDOCK_CONFIG_NAME)
        )

        # get sagify_module_path name
        mldock_config = mldock_manager.get_config()

        _ = WorkingDirectoryManager(base_dir=project_directory)

        # create routines
        routine_config_manager = RoutinesConfigManager(
            config=mldock_config.get("routines", {})
        )

        # ask for routines
        routine_config_manager.ask_for_routines()
        mldock_manager.update_routines(stages=routine_config_manager.get_config())

        # create stages config
        stage_config_manager = StageConfigManager(
            config=mldock_config.get("stages", {})
        )

        stage_config_manager.ask_for_stages()
        mldock_manager.update_stages(stages=stage_config_manager.get_config())

        mldock_manager.write_file()

        click.clear()
        logger.info(obj["logo"])
        states = mldock_manager.get_state()

        for state in states:
            click.echo(click.style(state["name"], bg="blue"), nl=True)
            click.echo(click.style(state["message"], fg="white"), nl=True)

        logger.info("\nlocal project was updated! ヽ(´▽`)/")
    except Exception as exception:
        logger.error(exception)
        raise


def add_commands(cli_group: click.group):
    """
    add commands to cli group
    args:
        cli (click.group)
    """
    cli_group.add_command(manage)


add_commands(stages)

