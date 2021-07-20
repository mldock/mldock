"""TEMPLATES COMMANDS"""
import logging
from pathlib import Path
import click

from mldock.platform_helpers import utils

click.disable_unicode_literals_warning = True
logger = logging.getLogger('mldock')
MLDOCK_CONFIG_NAME = 'mldock.json'


@click.group()
def templates():
    """
    Commands to create, update and manage container projects and templates.
    """

@click.command()
@click.option(
    '--name',
    help='Container name, used to name directories,etc.',
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
    '--out',
    help='Destination of template should be stored once created.',
    required=True,
    type=str
)
def create(name, project_directory, out):
    """
    Command to create a mldock enabled container template
    """

    try:
        if not Path(project_directory, MLDOCK_CONFIG_NAME).exists():
            raise Exception((
                "Path '{}' was not an mldock project. "
                "Confirm this directory is correct, otherwise "
                "create one.".format(project_directory)
            ))

        mldock_src_path = Path(project_directory, 'src')

        destination_path = Path(out, name)
        destination_path.mkdir(parents=False, exist_ok=True)

        destination_src_path = Path(destination_path, 'src')

        utils._copy_boilerplate_to_dst(mldock_src_path, destination_src_path)
    except Exception as exception:
        logger.error(exception)
        raise

templates.add_command(create)
