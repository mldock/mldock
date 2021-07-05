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
            ModelConfigManager, EnvironmentConfigManager, CliConfigureManager

from mldock.platform_helpers import utils
from mldock.platform_helpers.mldock import utils as mldock_utils
from mldock.api.templates import init_from_template

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
@click.option('--dir', help='Set the working directory for your sagify container.', required=True)
@click.option('--no-prompt', is_flag=True, help='Do not prompt user, instead use the mldock config to initialize the container.')
@click.option('--container-only', is_flag=True, help='Only inject new container assets.')
@click.option('--template', default=None, help='Directory containing mldock supported container to use to initialize the container.')
@click.pass_obj
def init(obj, dir, no_prompt, container_only, template):
    """
    Command to initialize mldock enabled container project
    """
    reset_terminal()
    mldock_package_path = obj['mldock_package_path']
    try:
        click.secho("Initializing MLDock project configuration", bg='blue', nl=True)

        if not Path(dir).is_dir():
            create_new = click.prompt('No MLDOCK project found. Create?', type=bool)

        mldock_manager = MLDockConfigManager(
            filepath=os.path.join(dir, MLDOCK_CONFIG_NAME),
            create=create_new
        )

        if template is not None:
            mldock_manager.update_config(template=template)

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

        # Get template specific files
        template = mldock_config["template"] if template is None else templates

        config_manager = CliConfigureManager()
        templates = config_manager.templates

        # get configured template server metadata
        # if not set, default to package default templates
        templates_root = templates.get('templates_root', Path(mldock_package_path, 'templates'))
        # if not set, default to local
        template_server = templates.get('server_type', 'local')

        init_from_template(
            template_name=template,
            templates_root=templates_root,
            src_directory=src_directory,
            container_only=container_only,
            template_server=template_server
        )

        # reset_terminal()
        # logger.info(obj["logo"])
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
    cli.add_command(summary)

add_commands(container)
