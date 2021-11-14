"""TEMPLATES COMMANDS"""
import mimetypes
import logging
from pathlib import Path
import click

from mldock.config_managers.cli import InputDataConfigManager, CliConfigureManager
from mldock.config_managers.container import MLDockConfigManager
from mldock.terminal import ProgressLogger
from mldock.platform_helpers.mldock.storage.pyarrow import (
    upload_assets,
    download_assets,
)
from mldock.api.assets import infer_filesystem_type

click.disable_unicode_literals_warning = True
logger = logging.getLogger("mldock")
MLDOCK_CONFIG_NAME = "mldock.json"


@click.group()
def datasets():
    """
    Commands to create, update and manage datasets for container projects
    """


@click.command()
@click.option(
    "--channel",
    help="asset channel name. Directory name, within project data/ to store assets",
    required=True,
    type=str,
)
@click.option(
    "--name",
    help="asset filename name. File name, within project data/<channel> in which data artifact will be found",
    required=True,
    type=str,
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
@click.option(
    "--remote", help="mldock remote to use to store or fetch dataset", type=str
)
@click.option("--remote_path", help="relative path within remote to store", type=str)
@click.option("--mime_type", "--type", help="type of file based on mimetypes", type=str)
@click.option(
    "--compression",
    help="type of file based on mimetypes",
    type=click.Choice(["zip", None], case_sensitive=False),
)
def create(
    channel, name, project_directory, remote, remote_path, mime_type, compression
):
    """
    Command to create dataset manifest for mldock enabled container projects.
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

        if mime_type is None:
            mime_type = mimetypes.guess_type(name)
            if isinstance(mime_type, (list, tuple)):
                mime_type = mime_type[0]

        if remote_path is None:
            remote_path = channel

        mldock_manager = MLDockConfigManager(
            filepath=Path(project_directory, MLDOCK_CONFIG_NAME)
        )

        # get mldock_module_dir name
        mldock_config = mldock_manager.get_config()

        input_data_channels = InputDataConfigManager(
            config=mldock_config.get("data", []),
            base_path=Path(project_directory, "data"),
        )

        input_data_channels.add_asset(
            channel=channel,
            filename=name,
            type=mime_type,
            remote=remote,
            compression=compression,
            remote_path=remote_path,
        )
        input_data_channels.write_gitignore()
        mldock_manager.update_data_channels(data=input_data_channels.get_config())

        mldock_manager.write_file()

    except Exception as exception:
        logger.error(exception)
        raise


@click.command()
@click.option(
    "--channel",
    help="asset channel name. Directory name, within project data/ to store assets",
    required=True,
    type=str,
)
@click.option(
    "--name",
    help="asset filename name. File name, within project data/<channel> in which data artifact will be found",
    required=True,
    type=str,
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
@click.option(
    "--remote", help="mldock remote to use to store or fetch dataset", type=str
)
@click.option("--remote_path", help="relative path within remote to store", type=str)
@click.option("--mime_type", "--type", help="type of file based on mimetypes", type=str)
@click.option(
    "--compression",
    help="type of file based on mimetypes",
    type=click.Choice(["zip", None], case_sensitive=False),
)
def update(
    channel, name, project_directory, remote, remote_path, mime_type, compression
):
    """
    Command to create dataset manifest for mldock enabled container projects.
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

        if mime_type is None:
            mime_type = mimetypes.guess_type(name)
            if isinstance(mime_type, (list, tuple)):
                mime_type = mime_type[0]

        if remote_path is None:
            remote_path = channel

        mldock_manager = MLDockConfigManager(
            filepath=Path(project_directory, MLDOCK_CONFIG_NAME)
        )

        # get mldock_module_dir name
        mldock_config = mldock_manager.get_config()

        input_data_channels = InputDataConfigManager(
            config=mldock_config.get("data", []),
            base_path=Path(project_directory, "data"),
        )

        input_data_channels.add_asset(
            channel=channel,
            filename=name,
            type=mime_type,
            remote=remote,
            compression=compression,
            remote_path=remote_path,
            update=True,
        )
        input_data_channels.write_gitignore()
        mldock_manager.update_data_channels(data=input_data_channels.get_config())

        mldock_manager.write_file()

    except Exception as exception:
        logger.error(exception)
        raise


@click.command()
@click.option(
    "--channel",
    help="asset channel name. Directory name, within project data/ to store assets",
    required=True,
    type=str,
)
@click.option(
    "--name",
    help="asset filename name. File name, within project data/<channel> in which data artifact will be found",
    required=True,
    type=str,
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
def remove(channel, name, project_directory):
    """
    Command to create dataset manifest for mldock enabled container projects.
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

        mldock_manager = MLDockConfigManager(
            filepath=Path(project_directory, MLDOCK_CONFIG_NAME)
        )

        # get mldock_module_dir name
        mldock_config = mldock_manager.get_config()

        input_data_channels = InputDataConfigManager(
            config=mldock_config.get("data", []),
            base_path=Path(project_directory, "data"),
        )

        input_data_channels.remove(channel=channel, filename=name)
        input_data_channels.write_gitignore()
        mldock_manager.update_data_channels(data=input_data_channels.get_config())

        mldock_manager.write_file()

    except Exception as exception:
        logger.error(exception)
        raise


@click.command()
@click.option(
    "--channel",
    help="asset channel name. Directory name, within project data/ to store assets",
    required=True,
    type=str,
)
@click.option(
    "--name",
    help="asset filename name. File name, within project data/<channel> in which data artifact will be found",
    required=True,
    type=str,
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
def push(channel, name, project_directory):
    """
    Command to create dataset manifest for mldock enabled container projects.
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

        mldock_manager = MLDockConfigManager(
            filepath=Path(project_directory, MLDOCK_CONFIG_NAME)
        )

        # get mldock_module_dir name
        mldock_config = mldock_manager.get_config()

        input_data_channels = InputDataConfigManager(
            config=mldock_config.get("data", []),
            base_path=Path(project_directory, "data"),
        )

        dataset = input_data_channels.get(channel=channel, filename=name)

        config_manager = CliConfigureManager()

        remote = config_manager.remotes.get(name=dataset["remote"])

        file_system, fs_base_path = infer_filesystem_type(remote["path"])

        with ProgressLogger(
            group="Upload",
            text="Uploading data artifacts",
            spinner="dots",
            on_success="Successfully uploaded model artifacts",
        ) as spinner:
            upload_assets(
                file_system=file_system,
                fs_base_path=fs_base_path,
                local_path=Path(
                    project_directory, "data", dataset["channel"]
                ).as_posix(),
                storage_location=Path("data", dataset["remote_path"]).as_posix(),
                zip_artifacts=dataset.get("compression", None) == "zip",
            )
            spinner.stop()

    except Exception as exception:
        logger.error(exception)
        raise


@click.command()
@click.option(
    "--channel",
    help="asset channel name. Directory name, within project data/ to store assets",
    required=True,
    type=str,
)
@click.option(
    "--name",
    help="asset filename name. File name, within project data/<channel> in which data artifact will be found",
    required=True,
    type=str,
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
def pull(channel, name, project_directory):
    """
    Command to create dataset manifest for mldock enabled container projects.
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

        mldock_manager = MLDockConfigManager(
            filepath=Path(project_directory, MLDOCK_CONFIG_NAME)
        )

        # get mldock_module_dir name
        mldock_config = mldock_manager.get_config()

        input_data_channels = InputDataConfigManager(
            config=mldock_config.get("data", []),
            base_path=Path(project_directory, "data"),
        )

        dataset = input_data_channels.get(channel=channel, filename=name)

        config_manager = CliConfigureManager()

        remote = config_manager.remotes.get(name=dataset["remote"])

        file_system, fs_base_path = infer_filesystem_type(remote["path"])

        with ProgressLogger(
            group="Download",
            text="Downloading data artifacts",
            spinner="dots",
            on_success="Successfully downloaded model artifacts",
        ) as spinner:

            download_assets(
                file_system=file_system,
                fs_base_path=fs_base_path,
                storage_location=Path("data", dataset["remote_path"]).as_posix(),
                local_path=Path(
                    project_directory, "data", dataset["channel"]
                ).as_posix(),
            )
            spinner.stop()

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
    cli_group.add_command(push)
    cli_group.add_command(pull)


add_commands(datasets)
