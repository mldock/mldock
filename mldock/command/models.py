"""TEMPLATES COMMANDS"""
import mimetypes
import logging
from pathlib import Path
import click

from mldock.config_managers.cli import ModelConfigManager
from mldock.config_managers.container import \
    MLDockConfigManager

click.disable_unicode_literals_warning = True
logger = logging.getLogger('mldock')
MLDOCK_CONFIG_NAME = 'mldock.json'


@click.group()
def models():
    """
    Commands to create, update and manage models for container projects
    """

@click.command()
@click.option(
    '--channel',
    help='asset channel name. Directory name, within project model/ to store assets',
    required=True,
    type=str
)
@click.option(
    '--name',
    help='asset filename name. File name, within project model/<channel> in which model artifact will be found',
    required=True,
    type=str
)
@click.option(
    '--project_directory',
    '--dir',
    '-d',
    help='mldock container project.',
    required=True,
    type=click.Path(
        exists=False,
        file_okay=False,
        dir_okay=True,
        writable=True,
        readable=True,
        resolve_path=False,
        allow_dash=False,
        path_type=None
    )
)
@click.option(
    '--remote',
    help='mldock remote to use to store or fetch dataset',
    type=str
)
@click.option(
    '--mime_type',
    '--type',
    help='type of file based on mimetypes',
    type=str
)
@click.option(
    '--compression',
    help='type of file based on mimetypes',
    type=click.Choice(
        ['zip', None],
        case_sensitive=False
    )
)
def create(channel, name, project_directory, remote, mime_type, compression):
    """
    Command to create models manifest for mldock enabled container projects.
    """

    try:
        if not Path(project_directory, MLDOCK_CONFIG_NAME).exists():
            raise Exception((
                "Path '{}' was not an mldock project. "
                "Confirm this directory is correct, otherwise "
                "create one.".format(project_directory)
            ))

        if mime_type is None:
            mime_type = mimetypes.guess_type(name)

        mldock_manager = MLDockConfigManager(
            filepath=Path(project_directory, MLDOCK_CONFIG_NAME)
        )

        # get mldock_module_dir name
        mldock_config = mldock_manager.get_config()

        input_data_channels = ModelConfigManager(
            config=mldock_config.get('model', []),
            base_path=Path(project_directory, 'model')
        )

        input_data_channels.add_asset(
            channel=channel,
            filename=name,
            type=mime_type,
            remote=remote,
            compression=compression
        )
        input_data_channels.write_gitignore()
        mldock_manager.update_data_channels(data=input_data_channels.get_config())

        mldock_manager.write_file()


    except Exception as exception:
        logger.error(exception)
        raise

@click.command()
@click.option(
    '--channel',
    help='asset channel name. Directory name, within project model/ to store assets',
    required=True,
    type=str
)
@click.option(
    '--name',
    help='asset filename name. File name, within project model/<channel> in which model artifact will be found',
    required=True,
    type=str
)
@click.option(
    '--project_directory',
    '--dir',
    '-d',
    help='mldock container project.',
    required=True,
    type=click.Path(
        exists=False,
        file_okay=False,
        dir_okay=True,
        writable=True,
        readable=True,
        resolve_path=False,
        allow_dash=False,
        path_type=None
    )
)
@click.option(
    '--remote',
    help='mldock remote to use to store or fetch dataset',
    type=str
)
@click.option(
    '--mime_type',
    '--type',
    help='type of file based on mimetypes',
    type=str
)
@click.option(
    '--compression',
    help='type of file based on mimetypes',
    type=click.Choice(
        ['zip', None],
        case_sensitive=False
    )
)
def update(channel, name, project_directory, remote, mime_type, compression):
    """
    Command to create models manifest for mldock enabled container projects.
    """

    try:
        if not Path(project_directory, MLDOCK_CONFIG_NAME).exists():
            raise Exception((
                "Path '{}' was not an mldock project. "
                "Confirm this directory is correct, otherwise "
                "create one.".format(project_directory)
            ))

        if mime_type is None:
            mime_type = mimetypes.guess_type(name)
            if isinstance(mime_type, (list, tuple)):
                mime_type = mime_type[0]

        mldock_manager = MLDockConfigManager(
            filepath=Path(project_directory, MLDOCK_CONFIG_NAME)
        )

        # get mldock_module_dir name
        mldock_config = mldock_manager.get_config()

        input_data_channels = ModelConfigManager(
            config=mldock_config.get('model', []),
            base_path=Path(project_directory, 'model')
        )

        input_data_channels.add_asset(
            channel=channel,
            filename=name,
            type=mime_type,
            remote=remote,
            compression=compression,
            update=True
        )
        input_data_channels.write_gitignore()
        mldock_manager.update_data_channels(data=input_data_channels.get_config())

        mldock_manager.write_file()


    except Exception as exception:
        logger.error(exception)
        raise

@click.command()
@click.option(
    '--channel',
    help='asset channel name. Directory name, within project model/ to store assets',
    required=True,
    type=str
)
@click.option(
    '--name',
    help='asset filename name. File name, within project model/<channel> in which model artifact will be found',
    required=True,
    type=str
)
@click.option(
    '--project_directory',
    '--dir',
    '-d',
    help='mldock container project.',
    required=True,
    type=click.Path(
        exists=False,
        file_okay=False,
        dir_okay=True,
        writable=True,
        readable=True,
        resolve_path=False,
        allow_dash=False,
        path_type=None
    )
)
def remove(channel, name, project_directory):
    """
    Command to create models manifest for mldock enabled container projects.
    """

    try:
        if not Path(project_directory, MLDOCK_CONFIG_NAME).exists():
            raise Exception((
                "Path '{}' was not an mldock project. "
                "Confirm this directory is correct, otherwise "
                "create one.".format(project_directory)
            ))

        mldock_manager = MLDockConfigManager(
            filepath=Path(project_directory, MLDOCK_CONFIG_NAME)
        )

        # get mldock_module_dir name
        mldock_config = mldock_manager.get_config()

        input_data_channels = ModelConfigManager(
            config=mldock_config.get('model', []),
            base_path=Path(project_directory, 'model')
        )

        input_data_channels.remove(
            channel=channel,
            filename=name
        )
        input_data_channels.write_gitignore()
        mldock_manager.update_data_channels(data=input_data_channels.get_config())

        mldock_manager.write_file()


    except Exception as exception:
        logger.error(exception)
        raise

def add_commands(cli_group: click.group):
    """
        add commands to cli group
        args:
            cli (click.group)
    """
    cli_group.add_command(create)
    cli_group.add_command(update)
    cli_group.add_command(remove)

add_commands(models)
