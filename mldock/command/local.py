"""LOCAL COMMANDS"""
import os
import sys
import json
from pathlib import Path
import logging
import subprocess
import click

from mldock.config_managers.cli import CliConfigureManager
import mldock.api.predict as predict_request
from mldock.terminal import (
    ChoiceWithNumbers,
    style_dropdown,
    style_2_level_detail,
    ProgressLogger,
    pretty_build_logs,
)
from mldock.platform_helpers.mldock import utils as mldock_utils
from mldock.config_managers.project import MLDockConfigManager
from mldock.api.local import (
    search_mldock_containers,
    docker_build,
    train_model,
    deploy_model,
)

click.disable_unicode_literals_warning = True
logger = logging.getLogger("mldock")
MLDOCK_CONFIG_NAME = "mldock.json"


def run_script_interactively(cmd, **kwargs):
    """Basic runner script for local interactive script execution"""
    output = subprocess.check_output(cmd, **kwargs)
    logger.info(output)


def python_executable():
    """Return the real path for the Python executable, if it exists.
    Return RuntimeError otherwise.
    Returns:
        (str): The real path of the current Python executable.
    """
    if not sys.executable:
        raise RuntimeError(
            "Failed to retrieve the real path for the Python executable binary"
        )
    return sys.executable


@click.group()
def local():
    """
    Commands for local development
    """


@click.command()
@click.option(
    "--project_directory",
    "--dir",
    "-d",
    help="mldock container project.",
    required=True,
    type=click.Path(
        exists=True,
        file_okay=False,
        dir_okay=True,
        writable=True,
        readable=True,
        resolve_path=False,
        allow_dash=False,
        path_type=None,
    ),
)
@click.option("--no-cache", help="builds container from scratch", is_flag=True)
@click.option("--tag", help="docker tag", type=str, default="latest")
@click.option("--stage", help="environment to stage.")
def build(project_directory, no_cache, tag, stage):
    """Command to build container locally"""
    mldock_manager = MLDockConfigManager(
        filepath=os.path.join(project_directory, MLDOCK_CONFIG_NAME)
    )
    # get mldock_module_dir name
    mldock_config = mldock_manager.get_config()
    image_name = mldock_config.get("image_name", None)
    template_name = mldock_config.get("template", None)
    container_dir = mldock_config.get("container_dir", None)
    module_path = os.path.join(
        project_directory,
        mldock_config.get("mldock_module_dir", "src"),
    )
    dockerfile_path = os.path.join(
        project_directory,
        mldock_config.get("mldock_module_dir", "src"),
        container_dir,
        "Dockerfile",
    )
    requirements_file_path = os.path.join(
        project_directory, mldock_config.get("requirements_dir", "requirements.txt")
    )

    with ProgressLogger(
        group="Stages",
        text="Retrieving Stages",
        spinner="dots",
        on_success="Stages Retrieved",
    ) as spinner:
        stages = mldock_config.get("stages", None)

        if stage is not None:
            tag = stages[stage]["tag"]

        if tag is None:
            raise Exception(
                "tag is not valid. Either choose a stage or set a tag manually"
            )

    try:
        with ProgressLogger(group="Build", text="Building", spinner="dots") as spinner:
            logs = docker_build(
                image_name=image_name,
                dockerfile_path=dockerfile_path,
                module_path=module_path,
                target_dir_name=mldock_config.get("mldock_module_dir", "src"),
                requirements_file_path=requirements_file_path,
                no_cache=no_cache,
                docker_tag=tag,
                container_platform=template_name,
            )
            for line in logs:

                spinner.info(pretty_build_logs(line=line))

                spinner.start()

    except Exception as exception:
        logger.error(exception)
        raise


from enum import Enum


class AuthType(Enum):

    BEARER = "bearer"


@click.command()
@click.option(
    "--payload",
    help="Path to payload",
    required=True,
    type=click.Path(
        exists=True,
        file_okay=True,
        dir_okay=False,
        writable=False,
        readable=True,
        resolve_path=False,
        allow_dash=False,
        path_type=None,
    ),
)
@click.option(
    "--request-content-type",
    default="application/json",
    help="format of payload",
    type=click.Choice(
        ["application/json", "text/csv", "image/jpeg"], case_sensitive=False
    ),
)
@click.option(
    "--response",
    help="Path to payload",
    type=click.Path(
        exists=True,
        file_okay=True,
        dir_okay=False,
        writable=False,
        readable=True,
        resolve_path=False,
        allow_dash=False,
        path_type=None,
    ),
)
@click.option(
    "--response-content-type",
    default="application/json",
    help="format of payload",
    type=click.Choice(
        ["application/json", "text/csv", "image/jpeg"], case_sensitive=False
    ),
)
@click.option(
    "--host",
    help="host url at which model is served",
    type=str,
    default="http://127.0.0.1:8080/invocations",
)
@click.option(
    "--headers",
    help="(Optional) Authentication to use for request",
    type=click.STRING,
    multiple=True,
)
def predict(payload, host, **kwargs):
    """
    Command to execute prediction request against ml endpoint
    """
    headers = {}

    for header in kwargs.get("headers"):
        headers.update(json.loads(header))

    with ProgressLogger(group="Predict", text="Running Request", spinner="dots"):
        if payload is None:
            logger.info(
                "\nPayload cannot be None. Please provide path to payload file."
            )
        else:
            pretty_output = predict_request.handle_prediction(
                host=host,
                request=payload,
                response_file=kwargs.get("response"),
                request_content_type=kwargs.get(
                    "request_content_type", "application/json"
                ),
                response_content_type=kwargs.get(
                    "response_content_type", "application/json"
                ),
                headers=headers,
            )
            logger.info(pretty_output)


@click.command()
@click.option(
    "--project_directory",
    "--dir",
    "-d",
    help="mldock container project.",
    required=True,
    type=click.Path(
        exists=True,
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
    "--params",
    "-p",
    help="(Optional) Hyperparameter override when running container.",
    nargs=2,
    type=click.Tuple([str, str]),
    multiple=True,
)
@click.option(
    "--env_vars",
    "-e",
    help="(Optional) Environment Variables override when running container.",
    nargs=2,
    type=click.Tuple([str, str]),
    multiple=True,
)
@click.option("--tag", help="docker tag", type=str, default="latest")
@click.option("--stage", help="environment to stage.")
@click.option("--interactive", help="run workflow without docker", is_flag=True)
def train(project_directory, **kwargs):
    """
    Command to run training locally on localhost
    """
    params = kwargs.get("params", None)
    env_vars = kwargs.get("env_vars", None)
    tag = kwargs.get("tag", None)
    stage = kwargs.get("stage", None)
    interactive = kwargs.get("interactive", False)

    mldock_manager = MLDockConfigManager(
        filepath=os.path.join(project_directory, MLDOCK_CONFIG_NAME)
    )
    # get mldock_module_path name
    mldock_config = mldock_manager.get_config()
    image_name = mldock_config.get("image_name", None)

    with ProgressLogger(
        group="Stages",
        text="Retrieving Stages",
        spinner="dots",
        on_success="Stages Retrieved",
    ) as spinner:
        stages = mldock_config.get("stages", "null")

        if stage is not None:
            tag = stages[stage]["tag"]

        if tag is None:
            raise Exception(
                "tag is not valid. Either choose a stage or set a tag manually"
            )

    with ProgressLogger(
        group="Environment",
        text="Retrieving Environment Varaiables",
        spinner="dots",
        on_success="Environment Ready",
    ) as spinner:
        project_env_vars = mldock_config.get("environment", {})
        for env_var in env_vars:
            key_, value_ = env_var
            project_env_vars.update({key_: value_})

        hyperparameters = mldock_config.get("hyperparameters", {})

        # override hyperparameters
        for param in params:
            key_, value_ = param
            hyperparameters.update({key_: value_})

        env_vars = mldock_utils.collect_mldock_environment_variables(
            stage=stage, hyperparameters=hyperparameters, **project_env_vars
        )

        config_manager = CliConfigureManager()
        env_vars.update(config_manager.local.get("environment", {}))

    with ProgressLogger(
        group="Training", text="Running Training", spinner="dots"
    ) as spinner:

        spinner.info("Training Environment = {}".format(env_vars))
        spinner.start()
        if interactive:
            spinner.info("Running interactively")
            spinner.start()
            # just run python src/container/prediction/serve.py
            base_ml_path = project_directory
            # must update /opt/ml working directory before running
            # perhaps setting from environment would be the best
            env_vars.update(
                {
                    "MLDOCK_BASE_DIR": Path(base_ml_path).absolute().as_posix(),
                    "MLDOCK_INPUT_DIR": ".",
                }
            )

            # subprocess only supports 'ascii' supported str for environment variables
            env_vars = mldock_utils.format_dict_for_subprocess(env_vars)
            script_path = "src/container/training/train.py"
            run_script_interactively(
                [python_executable(), script_path], cwd=base_ml_path, env=env_vars
            )
        else:
            spinner.info("Running docker container")
            spinner.start()
            train_model(
                working_dir=project_directory,
                docker_tag=tag,
                image_name=image_name,
                entrypoint="src/container/executor.sh",
                cmd="train",
                env=env_vars,
            )


@click.command()
@click.option(
    "--project_directory",
    "--dir",
    "-d",
    help="mldock container project.",
    required=True,
    type=click.Path(
        exists=True,
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
    "--params",
    "-p",
    help="(Optional) Hyperparameter override when running container.",
    nargs=2,
    type=click.Tuple([str, str]),
    multiple=True,
)
@click.option(
    "--env_vars",
    "-e",
    help="(Optional) Environment Variables override when running container.",
    nargs=2,
    type=click.Tuple([str, str]),
    multiple=True,
)
@click.option("--tag", help="docker tag", type=str, default="latest")
@click.option(
    "--port", help="host url at which model is served", type=str, default="8080"
)
@click.option("--stage", help="environment to stage.")
@click.option("--interactive", help="run workflow without docker", is_flag=True)
@click.pass_obj
def deploy(obj, project_directory, **kwargs):
    """
    Command to deploy ml container on localhost
    """
    params = kwargs.get("params", None)
    env_vars = kwargs.get("env_vars", None)
    tag = kwargs.get("tag", None)
    port = kwargs.get("port", None)
    stage = kwargs.get("stage", None)
    interactive = kwargs.get("interactive", False)

    verbose = obj.get("verbose", False)
    mldock_manager = MLDockConfigManager(
        filepath=os.path.join(project_directory, MLDOCK_CONFIG_NAME)
    )
    # get mldock_module_path name
    mldock_config = mldock_manager.get_config()
    image_name = mldock_config.get("image_name", None)

    with ProgressLogger(
        group="Stages",
        text="Retrieving Stages",
        spinner="dots",
        on_success="Stages Retrieved",
    ) as spinner:
        stages = mldock_config.get("stages", None)

        if stage is not None:
            tag = stages[stage]["tag"]

        if tag is None:
            raise Exception(
                "tag is not valid. Either choose a stage or set a tag manually"
            )

    project_env_vars = mldock_config.get("environment", {})

    for env_var in env_vars:
        key_, value_ = env_var
        print(key_, value_)
        project_env_vars.update({key_: value_})

    hyperparameters = mldock_config.get("hyperparameters", {})

    # override hyperparameters
    for param in params:
        key_, value_ = param
        print(key_, value_)
        hyperparameters.update({key_: value_})

    env_vars = mldock_utils.collect_mldock_environment_variables(
        stage=stage,
        hyperparameters=mldock_config.get("hyperparameters", {}),
        **project_env_vars
    )

    config_manager = CliConfigureManager()
    env_vars.update(config_manager.local.get("environment", {}))

    with ProgressLogger(
        group="Deploy",
        text="Deploying model to {} @ localhost".format(port),
        spinner="dots",
    ) as spinner:
        spinner.info("Deployment Environment = {}".format(env_vars))
        spinner.start()
        if interactive:
            spinner.info("Running interactively")
            spinner.start()
            # just run python src/container/prediction/serve.py
            base_ml_path = project_directory
            # must update /opt/ml working directory before running
            # perhaps setting from environment would be the best
            # check out the python runner from sagemaker_training
            env_vars.update(
                {
                    "MLDOCK_BASE_DIR": Path(base_ml_path).absolute().as_posix(),
                    "MLDOCK_INPUT_DIR": ".",
                }
            )

            # subprocess only supports 'ascii' supported str for environment variables
            env_vars = mldock_utils.format_dict_for_subprocess(env_vars)

            script_path = "src/container/prediction/serve.py"

            run_script_interactively(
                [python_executable(), script_path], cwd=base_ml_path, env=env_vars
            )
        else:
            spinner.info("Running docker container")
            spinner.start()

            deploy_model(
                working_dir=project_directory,
                docker_tag=tag,
                image_name=image_name,
                port={8080: port},
                entrypoint="src/container/executor.sh",
                cmd="serve",
                env=env_vars,
                verbose=verbose,
            )


@click.command()
def stop():
    """
    Command to stop ml container on localhost
    """

    try:
        containers = search_mldock_containers()

        tags = [
            style_2_level_detail(major_detail=c.image.tags[0], minor_detail=c.name)
            for c in containers
        ] + ["abort"]
        # newline break
        click.echo("")
        click.secho("Running MLDock containers:", bg="blue", nl=True)
        container_tag = click.prompt(
            text=style_dropdown(
                group_name="container name", options=tags, default="abort"
            ),
            type=ChoiceWithNumbers(tags, case_sensitive=False),
            show_default=False,
            default="abort",
            show_choices=False,
        )

        for container in containers:
            for image_tag in container.image.tags:
                if image_tag in container_tag:
                    # make newline
                    click.echo("")
                    project_container_tag = click.style(container_tag, fg="bright_blue")
                    if click.confirm(
                        "Stop the running container = {}?".format(project_container_tag)
                    ):
                        container.kill()

                    break

    except Exception as exception:
        logger.error(exception)
        raise


def add_commands(cli_group: click.group):
    """
    add commands to cli group
    args:
        cli (click.group)
    """
    cli_group.add_command(build)
    cli_group.add_command(predict)
    cli_group.add_command(train)
    cli_group.add_command(deploy)
    cli_group.add_command(stop)


add_commands(local)
