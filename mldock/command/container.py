import os
import sys
import json
import logging
import click
from pathlib import Path
from future.moves import subprocess

from mldock.config_managers.core import WorkingDirectoryManager
from mldock.config_managers.container import MLDockConfigManager
from mldock.config_managers.cli import \
    ResourceConfigManager, PackageConfigManager, \
        HyperparameterConfigManager, InputDataConfigManager, StageConfigManager, \
            ModelConfigManager, EnvironmentConfigManager
from mldock.platform_helpers import utils
from mldock.platform_helpers.mldock import utils as mldock_utils
from mldock.api.container import init_container_project

click.disable_unicode_literals_warning = True
logger=logging.getLogger('mldock')
MLDOCK_CONFIG_NAME='mldock.json'


def reset_terminal():
    # os.system("clear")
    click.clear()

@click.group()
def container():
    """
    Commands to create, update and manage container projects and templates.
    """
    pass

@click.command()
@click.option('--name', help='Container name, used to name directories,etc.', required=True, type=str)
@click.option('--dir', help='Relative name of MLDOCK project', required=True, type=str)
@click.option('--out', help='Destination of template should be stored once created.', required=True, type=str)
@click.pass_obj
def create_template(obj, name, dir, out):
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

@click.command()
@click.option('--dir', help='Set the working directory for your sagify container.', required=True)
@click.option('--testing-framework', default=None, help='(Optional) Pytest framework. This creates a few health-check tests')
@click.option('--service', default=None, help='(Optional) Docker Compose. This seeds a service config.')
@click.option('--no-prompt', is_flag=True, help='Do not prompt user, instead use the mldock config to initialize the container.')
@click.option('--container-only', is_flag=True, help='Only inject new container assets.')
@click.option('--template', default=None, help='Directory containing mldock supported container to use to initialize the container.')
@click.pass_obj
def init(obj, dir, testing_framework, service, no_prompt, container_only, template):
    """
    Command to initialize mldock enabled container project
    """
    reset_terminal()
    mldock_package_path=obj['mldock_package_path']
    try:
        click.secho("Initializing MLDock project configuration", bg='blue', nl=True)
        mldock_manager = MLDockConfigManager(
            filepath=os.path.join(dir, MLDOCK_CONFIG_NAME),
            create=True
        )
        if not no_prompt:
            mldock_manager.setup_config()

        package_manager = PackageConfigManager(
            filepath=os.path.join(dir, "requirements.txt"),
            create=True
        )
        # write to package manager
        package_manager.write_file()


        path_to_payload = Path(os.path.join(dir, "payload.json"))
        if not path_to_payload.exists():
            path_to_payload.write_text(json.dumps({"feature1": 10, "feature2":"groupA"}))

        # get sagify_module_path name
        mldock_config = mldock_manager.get_config()

        src_directory = os.path.join(
            dir,
            mldock_config.get("mldock_module_dir", "src")
        )
        mldock_module_path = os.path.join(
            src_directory,
            'container'
        )

        working_directory_manager = WorkingDirectoryManager(base_dir=dir)
        # sagemaker
        config_path = working_directory_manager.input_config_dir

        # create stages config
        stage_config_manager = StageConfigManager(
            config=mldock_config.get('stages', {})
        )
        # set input data channels
        input_data_channels = InputDataConfigManager(
            config=mldock_config.get('data', []),
            base_path=Path(dir, 'data')
        )

        # set model channels
        model_channels = ModelConfigManager(
            config=mldock_config.get('model', []),
            base_path=Path(dir, 'model')
        )

        # set hyperparameters
        hyperparameters = HyperparameterConfigManager(
            config=mldock_config.get('hyperparameters', {})
        )

        # set environment variables
        environment = EnvironmentConfigManager(
            config=mldock_config.get('environment', {})
        )

        if not no_prompt:
            stage_config_manager.ask_for_stages()
            # update stages
            mldock_manager.update_stages(stages=stage_config_manager.get_config())
            # update input data channels
            input_data_channels.ask_for_input_data_channels()
            input_data_channels.write_gitignore()
            mldock_manager.update_data_channels(data=input_data_channels.get_config())
            # update model channels
            model_channels.ask_for_model_channels()
            model_channels.write_gitignore()
            mldock_manager.update_model_channels(models=model_channels.get_config())
            # update hyperparameters
            hyperparameters.ask_for_hyperparameters()
            mldock_manager.update_hyperparameters(hyperparameters=hyperparameters.get_config())
            # update environments
            environment.ask_for_env_vars()
            mldock_manager.update_env_vars(environment=environment.get_config())

        mldock_manager.write_file()

        # Get platform specific files
        platform = mldock_config.get("platform", None)

        if platform == "sagemaker":
            # get list of dataset names
            mldock_data = mldock_config.get("data", None)
            input_config_config = mldock_utils._extract_data_channels_from_mldock(mldock_data)
            utils._write_json(input_config_config, Path(dir,'config/inputdataconfig.json'))
            utils._write_json({"current_host": "dummy_host", "hosts": ["dummy_host", "second_dummy_host"]}, Path(dir,'config/resourceconfig.json'))

        init_container_project(
            dir=working_directory_manager.get_working_dir(),
            mldock_package_path=mldock_package_path,
            mldock_config=mldock_config,
            testing_framework=testing_framework,
            service=service,
            container_only=container_only,
            template_dir=template
        )

        reset_terminal()
        logger.info(obj["logo"])
        states = mldock_manager.get_state()

        for state in states:
            click.echo(click.style(state["name"], bg='blue'), nl=True)
            click.echo(click.style(state["message"], fg='white'), nl=True)

        logger.info("\nlocal container volume is ready! ヽ(´▽`)/")
    except subprocess.CalledProcessError as exception:
        logger.error(exception)
        raise
    except Exception as exception:
        logger.error(exception)
        raise

@click.command()
@click.option('--dir', help='Set the working directory for your sagify container.', required=True)
@click.pass_obj
def update(obj, dir):
    """
    Command to update mldock container.
    """
    reset_terminal()
    try:
        logger.info("Loading MLDock config")
        mldock_manager = MLDockConfigManager(
            filepath=os.path.join(dir, MLDOCK_CONFIG_NAME)
        )

        # get sagify_module_path name
        mldock_config = mldock_manager.get_config()

        # get list of dataset names
        mldock_data = mldock_config.get("data", None)
        input_config_config = mldock_utils._extract_data_channels_from_mldock(mldock_data)

        src_directory = os.path.join(
            dir,
            mldock_config.get("mldock_module_dir", "src")
        )
        mldock_module_path = os.path.join(
            src_directory,
            'container'
        )

        working_directory_manager = WorkingDirectoryManager(base_dir=dir)
        # sagemaker
        config_path = working_directory_manager.input_config_dir

        # create stages config
        stage_config_manager = StageConfigManager(
            config=mldock_config.get('stages', {})
        )
        # set input data channels
        input_data_channels = InputDataConfigManager(
            config=mldock_config.get('data', []),
            base_path=Path(dir, 'data')
        )
        # set model channels
        model_channels = ModelConfigManager(
            config=mldock_config.get('model', []),
            base_path=Path(dir, 'model')
        )

        # set hyperparameters
        hyperparameters = HyperparameterConfigManager(
            config=mldock_config.get('hyperparameters', {})
        )

        # set environment variables
        environment = EnvironmentConfigManager(
            config=mldock_config.get('environment', {})
        )

        stage_config_manager.ask_for_stages()
        # update stages
        mldock_manager.update_stages(stages=stage_config_manager.get_config())
        # update input data channels
        input_data_channels.ask_for_input_data_channels()
        input_data_channels.write_gitignore()
        mldock_manager.update_data_channels(data=input_data_channels.get_config())
        # update model channels
        model_channels.ask_for_model_channels()
        model_channels.write_gitignore()
        mldock_manager.update_model_channels(models=model_channels.get_config())
        # update hyperparameters
        hyperparameters.ask_for_hyperparameters()
        mldock_manager.update_hyperparameters(hyperparameters=hyperparameters.get_config())
        # update environments
        environment.ask_for_env_vars()
        mldock_manager.update_env_vars(environment=environment.get_config())

        mldock_manager.write_file()

        # Get platform specific files
        platform = mldock_config.get("platform", None)

        if platform == "sagemaker":
            # get list of dataset names
            mldock_data = mldock_config.get("data", None)
            input_config_config = mldock_utils._extract_data_channels_from_mldock(mldock_data)
            utils._write_json(input_config_config, Path(dir,'config/inputdataconfig.json'))

        click.clear()
        logger.info(obj["logo"])
        states = mldock_manager.get_state()

        for state in states:
            click.echo(click.style(state["name"], bg='blue'), nl=True)
            click.echo(click.style(state["message"], fg='white'), nl=True)

        logger.info("\nlocal container was updated! ヽ(´▽`)/")
    except subprocess.CalledProcessError as exception:
        logger.error(exception)
        raise
    except Exception as exception:
        logger.error(exception)
        raise

@click.command()
@click.option('--dir', help='Set the working directory for your sagify container.', required=True)
@click.pass_obj
def summary(obj, dir):
    """
    Command to show summary for mldock container
    """
    try:
        logger.info("Loading MLDock config")
        mldock_manager = MLDockConfigManager(
            filepath=os.path.join(dir, MLDOCK_CONFIG_NAME)
        )

        states = mldock_manager.get_state()

        for state in states:
            click.echo(click.style(state["name"], bg='blue'), nl=True)
            click.echo(click.style(state["message"], fg='white'), nl=True)

        logger.info("\nlocal container was updated! ヽ(´▽`)/")
    except Exception as exception:
        logger.error(exception)
        raise

def add_commands(cli):
    """add cli commands to group"""
    cli.add_command(init)
    cli.add_command(update)
    cli.add_command(create_template)
    cli.add_command(summary)

add_commands(container)
