"""PACKAGES COMMANDS"""
import logging
from pathlib import Path
import click

from mldock.api.packages import build_wheels

click.disable_unicode_literals_warning = True
logger = logging.getLogger("mldock")
MLDOCK_CONFIG_NAME = "mldock.yaml"


@click.group()
def packages():
    """
    Commands to manage package dependencies in mldock projects
    """


@click.command(
    context_settings=dict(
        ignore_unknown_options=True,
    )
)
@click.option(
    "--project_directory",
    "--dir",
    "-d",
    help="mldock container project.",
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
@click.argument("pip_wheel_args", nargs=-1, type=click.UNPROCESSED)
def pack(project_directory, pip_wheel_args):
    """
    Command to create a mldock enabled container template
    """

    try:
        if not Path(project_directory, MLDOCK_CONFIG_NAME).exists():
            raise Exception(
                (
                    "Path '{}' was not an mldock project. "
                    "Confirm this directory is correct, otherwise "
                    "create one.".format(project_directory)
                )
            )

        mldock_src_path = Path(project_directory, "src")
        container_project_packages_path = Path(mldock_src_path, "packages").as_posix()

        build_wheels(
            dist_dir=container_project_packages_path,
            pip_wheel_args=list(pip_wheel_args),
        )
    except Exception as exception:
        logger.error(exception)
        raise


packages.add_command(pack)
