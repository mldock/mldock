"""CONTAINER PROJECT MANAGEMENT COMMANDS"""
import os
import json
from pathlib import Path
import logging
import click

from mldock.config_managers.core import WorkingDirectoryManager
from mldock.config_managers.container import MLDockConfigManager
from mldock.platform_helpers import utils
from mldock.config_managers.cli import (
    PackageConfigManager,
    HyperparameterConfigManager,
    InputDataConfigManager,
    StageConfigManager,
    ModelConfigManager,
    EnvironmentConfigManager,
    CliConfigureManager,
)

from mldock.api.templates import init_from_template, check_available_templates

click.disable_unicode_literals_warning = True
logger = logging.getLogger("mldock")
MLDOCK_CONFIG_NAME = "mldock.json"


def reset_terminal():
    """clears the terminal view frame"""
    click.clear()


@click.group()
def container():
    """
    Commands to create, update and manage container projects and templates.
    """


@click.command()
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
    "--no-prompt",
    is_flag=True,
    help="Do not prompt user, instead use the mldock config to initialize the container.",
)
@click.option(
    "--container-only", is_flag=True, help="Only inject new container assets."
)
@click.option(
    "--template",
    default=None,
    help="Directory containing mldock supported container to use to initialize the container.",
)
@click.option("--requirements", default=None, help="path to requirements file.")
@click.option(
    "--params",
    "-p",
    help="(Optional) Hyperparameter to be added in config.",
    nargs=2,
    type=click.Tuple([str, str]),
    multiple=True,
)
@click.option(
    "--env_vars",
    "-e",
    help="(Optional) Environment Variables to be added in config.",
    nargs=2,
    type=click.Tuple([str, str]),
    multiple=True,
)
@click.option(
    "--trainer-script",
    help="provide a path to your trainer script.",
    type=click.Path(
        exists=False,
        file_okay=True,
        dir_okay=False,
        writable=True,
        readable=True,
        resolve_path=False,
        allow_dash=False,
        path_type=None,
    ),
)
@click.option(
    "--prediction-script",
    help="provide a path to your prediction script.",
    type=click.Path(
        exists=False,
        file_okay=True,
        dir_okay=False,
        writable=True,
        readable=True,
        resolve_path=False,
        allow_dash=False,
        path_type=None,
    ),
)
@click.pass_obj
def init(obj, project_directory, **kwargs):
    """
    Command to initialize mldock enabled container project
    """
    no_prompt = kwargs.get("no_prompt", False)
    container_only = kwargs.get("container_only", False)
    template = kwargs.get("template", "generic")
    requirements = kwargs.get("requirements", None)
    params = kwargs.get("params", None)
    env_vars = kwargs.get("env_vars", None)
    trainer_script = kwargs.get("trainer_script", None)
    prediction_script = kwargs.get("prediction_script", None)

    reset_terminal()
    mldock_package_path = obj["mldock_package_path"]
    try:
        click.secho("Initializing MLDock project configuration", bg="blue", nl=True)

        if not Path(project_directory, "mldock.json").is_file():
            create_new = click.prompt(
                "No MLDOCK project found. Create?", type=bool, default="no"
            )
        else:
            create_new = False

        # check template config
        config_manager = CliConfigureManager()
        templates = config_manager.templates

        # get configured template server metadata
        # if not set, default to package default templates
        templates_root = templates.get(
            "templates_root", Path(mldock_package_path, "templates")
        )
        # if not set, default to local
        template_server = templates.get("server_type", "local")

        # get available templates
        available_templates = check_available_templates(
            templates_root=templates_root, template_server=template_server
        )

        mldock_manager = MLDockConfigManager(
            filepath=Path(project_directory, MLDOCK_CONFIG_NAME),
            create=create_new,
            available_templates=available_templates,
        )

        if not no_prompt:
            mldock_manager.setup_config()

        # get mldock config
        mldock_config = mldock_manager.get_config()

        if template is not None:
            mldock_manager.update_config(template=template)

        if params is not None:
            hyperparameters = mldock_config.get("hyperparameters", {})
            for param in params:
                key_, value_ = param
                hyperparameters.update({key_: value_})
            mldock_manager.update_config(hyperparameters=hyperparameters)

        if env_vars is not None:
            environment = mldock_config.get("environment", {})
            for env_var in env_vars:
                key_, value_ = env_var
                environment.update({key_: value_})
            mldock_manager.update_config(environment=environment)

        # finally delete original

        path_to_payload = Path(project_directory, "payload.json")
        if not path_to_payload.exists():
            path_to_payload.write_text(
                json.dumps({"feature1": 10, "feature2": "groupA"})
            )

        src_directory = os.path.join(
            project_directory, mldock_config.get("mldock_module_dir", "src")
        )

        _ = WorkingDirectoryManager(base_dir=project_directory)

        # create stages config
        stage_config_manager = StageConfigManager(
            config=mldock_config.get("stages", {})
        )
        # set input data channels
        input_data_channels = InputDataConfigManager(
            config=mldock_config.get("data", []),
            base_path=Path(project_directory, "data"),
        )

        # set model channels
        model_channels = ModelConfigManager(
            config=mldock_config.get("model", []),
            base_path=Path(project_directory, "model"),
        )

        # set hyperparameters
        hyperparameters = HyperparameterConfigManager(
            config=mldock_config.get("hyperparameters", {})
        )

        # set environment variables
        environment = EnvironmentConfigManager(
            config=mldock_config.get("environment", {})
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
            mldock_manager.update_hyperparameters(
                hyperparameters=hyperparameters.get_config()
            )
            # update environments
            environment.ask_for_env_vars()
            mldock_manager.update_env_vars(environment=environment.get_config())

        mldock_manager.write_file()

        # Get template specific files
        template = mldock_config["template"]

        init_from_template(
            template_name=template,
            templates_root=templates_root,
            src_directory=src_directory,
            container_only=container_only,
            template_server=template_server,
            trainer_script=trainer_script,
            prediction_script=prediction_script,
        )

        # always setup requirements in src/
        package_dir = mldock_manager.get_config().get(
            "requirements_dir", "src/requirements.txt"
        )
        requirement_file = Path(project_directory, package_dir)
        if requirements is not None:
            logger.info(f"Copying {requirements} => {requirement_file.as_posix()}")
            utils.copy_file(requirements, requirement_file)

        package_manager = PackageConfigManager(
            filepath=requirement_file, create=(requirement_file.is_file() == False)
        )
        package_manager.write_file()

        states = mldock_manager.get_state()

        for state in states:
            click.echo(click.style(state["name"], bg="blue"), nl=True)
            click.echo(click.style(state["message"], fg="white"), nl=True)

        logger.info("\nlocal container volume is ready! ヽ(´▽`)/")
    except Exception as exception:
        logger.error(exception)
        raise


@click.command()
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
@click.pass_obj
def update(obj, project_directory):
    """
    Command to update mldock container.
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

        # create stages config
        stage_config_manager = StageConfigManager(
            config=mldock_config.get("stages", {})
        )
        # set input data channels
        input_data_channels = InputDataConfigManager(
            config=mldock_config.get("data", []),
            base_path=Path(project_directory, "data"),
        )
        # set model channels
        model_channels = ModelConfigManager(
            config=mldock_config.get("model", []),
            base_path=Path(project_directory, "model"),
        )

        # set hyperparameters
        hyperparameters = HyperparameterConfigManager(
            config=mldock_config.get("hyperparameters", {})
        )

        # set environment variables
        environment = EnvironmentConfigManager(
            config=mldock_config.get("environment", {})
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
        mldock_manager.update_hyperparameters(
            hyperparameters=hyperparameters.get_config()
        )
        # update environments
        environment.ask_for_env_vars()
        mldock_manager.update_env_vars(environment=environment.get_config())

        mldock_manager.write_file()

        click.clear()
        logger.info(obj["logo"])
        states = mldock_manager.get_state()

        for state in states:
            click.echo(click.style(state["name"], bg="blue"), nl=True)
            click.echo(click.style(state["message"], fg="white"), nl=True)

        logger.info("\nlocal container was updated! ヽ(´▽`)/")
    except Exception as exception:
        logger.error(exception)
        raise


@click.command()
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
def summary(project_directory):
    """
    Command to show summary for mldock container
    """
    try:
        mldock_manager = MLDockConfigManager(
            filepath=os.path.join(project_directory, MLDOCK_CONFIG_NAME)
        )

        states = mldock_manager.get_state()

        for state in states:
            click.echo(click.style(state["name"], bg="blue"), nl=True)
            click.echo(click.style(state["message"], fg="white"), nl=True)

    except Exception as exception:
        logger.error(exception)
        raise


def add_commands(cli_group: click.group):
    """
    add commands to cli group
    args:
        cli (click.group)
    """
    cli_group.add_command(init)
    cli_group.add_command(update)
    cli_group.add_command(summary)


add_commands(container)
