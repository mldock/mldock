import os
import sys
import json
import logging
import click
from pathlib import Path

from mldock.platform_helpers import utils

click.disable_unicode_literals_warning = True
logger = logging.getLogger('mldock')
MLDOCK_CONFIG_NAME = 'mldock.json'


@click.group()
def templates():
    """
    Commands to create, update and manage container projects and templates.
    """
    pass

@click.command()
@click.option('--name', help='Container name, used to name directories,etc.', required=True, type=str)
@click.option('--dir', help='Relative name of MLDOCK project', required=True, type=str)
@click.option('--out', help='Destination of template should be stored once created.', required=True, type=str)
@click.pass_obj
def create(obj, name, dir, out):
    """
    Command to create a mldock enabled container template
    """

    try:
        if not Path(dir, MLDOCK_CONFIG_NAME).exists():
            raise Exception("Path '{}' was not an mldock project. Confirm this directory is correct, otherwise create one.".format(dir))

        mldock_src_path = Path(dir, 'src')

        destination_path = Path(out, name)
        destination_path.mkdir(parents=False, exist_ok=True)

        destination_src_path = Path(destination_path, 'src')

        utils._copy_boilerplate_to_dst(mldock_src_path, destination_src_path)
    except Exception as exception:
        logger.error(exception)
        raise

templates.add_command(create)
