import os
import sys
import json
import logging
import click
from pathlib import Path
from future.moves import subprocess

from mldock.config_managers.cli import \
    CliConfigureManager
import mldock.api.predict as predict_request
from mldock.terminal import \
    ChoiceWithNumbers, style_dropdown, style_2_level_detail, \
        ProgressLogger, pretty_build_logs
from mldock.platform_helpers.mldock import utils as mldock_utils
from mldock.config_managers.container import MLDockConfigManager
from mldock.api.local import \
    search_mldock_containers, docker_build, train_model, deploy_model

click.disable_unicode_literals_warning = True
logger = logging.getLogger('mldock')
MLDOCK_CONFIG_NAME = 'mldock.json'

@click.group()
def local():
    """
    Commands for local development
    """
    pass

@click.command()
@click.option('--dir', help='Set the working directory for your mldock container.', required=True)
@click.option('--no-cache', help='builds container from scratch', is_flag=True)
@click.option('--tag', help='docker tag', type=str, default='latest')
@click.option('--stage', help='environment to stage.')
@click.pass_obj
def build(obj, dir, no_cache, tag, stage):
    """Command to build container locally
    """
    mldock_manager = MLDockConfigManager(
        filepath=os.path.join(dir, MLDOCK_CONFIG_NAME)
    )
    # get mldock_module_dir name
    mldock_config = mldock_manager.get_config()
    image_name = mldock_config.get("image_name", None)
    template_name = mldock_config.get("template", None)
    container_dir = mldock_config.get("container_dir", None)
    module_path = os.path.join(
        dir,
        mldock_config.get("mldock_module_dir", "src"),
    )
    dockerfile_path = os.path.join(
        dir,
        mldock_config.get("mldock_module_dir", "src"),
        container_dir
    )
    requirements_file_path = os.path.join(
        dir,
        mldock_config.get("requirements_dir", "requirements.txt")
    )

    with ProgressLogger(
        group='Stages',
        text='Retrieving Stages',
        spinner='dots',
        on_success='Stages Retrieved'
    ) as spinner:
        stages = mldock_config.get("stages", None)

        if stage is not None:
            tag = stages[stage]['tag']

        if tag is None:
            raise Exception("tag is not valid. Either choose a stage or set a tag manually")

    try:
        with ProgressLogger(group='Build', text='Building', spinner='dots') as spinner:
            logs = docker_build(
                image_name=image_name,
                dockerfile_path=dockerfile_path,
                module_path=module_path,
                target_dir_name=mldock_config.get("mldock_module_dir", "src"),
                requirements_file_path=requirements_file_path,
                no_cache=no_cache,
                docker_tag=tag,
                container_platform=template_name
            )
            for line in logs:

                spinner.info(pretty_build_logs(line=line))

                spinner.start()

    except subprocess.CalledProcessError as exception:
        logger.error(exception)
        raise
    except Exception as exception:
        logger.error(exception)
        raise

@click.command()
@click.option('--payload', default=None, help='path to payload file', required=True)
@click.option('--content-type', default='application/json', help='format of payload', type=click.Choice(['application/json', 'text/csv', 'image/jpeg'], case_sensitive=False))
@click.option('--host', help='host url at which model is served', type=str, default='http://127.0.0.1:8080/invocations')
def predict(payload, content_type, host):
    """
    Command to execute prediction request against ml endpoint
    """
    with ProgressLogger(group='Predict', text='Running Request', spinner='dots') as spinner:
        if payload is None:
            logger.info("\nPayload cannot be None. Please provide path to payload file.")
        else:
            if content_type in ['application/json']:
                pretty_output = predict_request.send_json(filepath=payload, host=host)
            elif content_type in ['text/csv']:
                pretty_output = predict_request.send_csv(filepath=payload, host=host)
            elif content_type in ['image/jpeg']:
                pretty_output = predict_request.send_image_jpeg(filepath=payload, host=host)
            else:
                raise Exception("Content-type is not supported.")
            logger.info(pretty_output)

@click.command()
@click.option('--dir', help='Set the working directory for your mldock container.', required=True)
@click.option(
    '--params',
    '-p',
    help='(Optional) Hyperparameter override when running container.',
    nargs=2,
    type=click.Tuple([str, str]),
    multiple=True
)
@click.option(
    '--env_vars',
    '-e',
    help='(Optional) Environment Variables override when running container.',
    nargs=2,
    type=click.Tuple([str, str]),
    multiple=True
)
@click.option('--tag', help='docker tag', type=str, default='latest')
@click.option('--stage', help='environment to stage.')
@click.pass_obj
def train(obj, dir, params, env_vars, tag, stage):
    """
    Command to run training locally on localhost
    """
    mldock_manager = MLDockConfigManager(
        filepath=os.path.join(dir, MLDOCK_CONFIG_NAME)
    )
    # get mldock_module_path name
    mldock_config = mldock_manager.get_config()
    module_path = os.path.join(
        dir,
        mldock_config.get("mldock_module_dir", "src"),
    )
    image_name = mldock_config.get("image_name", None)
    container_dir = mldock_config.get("container_dir", None)

    with ProgressLogger(
        group='Stages',
        text='Retrieving Stages',
        spinner='dots',
        on_success='Stages Retrieved'
    ) as spinner:
        stages = mldock_config.get("stages", None)

        if stage is not None:
            tag = stages[stage]['tag']

        if tag is None:
            raise Exception("tag is not valid. Either choose a stage or set a tag manually")

    with ProgressLogger(
        group='Environment',
        text='Retrieving Environment Varaiables',
        spinner='dots',
        on_success='Environment Ready'
    ) as spinner:
        project_env_vars = mldock_config.get('environment', {})

        for env_var in env_vars:
            key_, value_ = env_var
            project_env_vars.update(
                {key_: value_}
            )

        hyperparameters = mldock_config.get('hyperparameters', {})

        # override hyperparameters
        for param in params:
            key_, value_ = param
            hyperparameters.update(
                {key_: value_}
            )

        env_vars = mldock_utils.collect_mldock_environment_variables(
            stage=stage,
            hyperparameters=hyperparameters,
            **project_env_vars
        )

        config_manager = CliConfigureManager()
        env_vars.update(
            config_manager.local.get('environment')
        )

    with ProgressLogger(
        group='Training',
        text='Running Training',
        spinner='dots'
    ) as spinner:

        spinner.info("Training Environment = {}".format(env_vars))
        spinner.start()

        train_model(
            working_dir=dir,
            docker_tag=tag,
            image_name=image_name,
            entrypoint="src/container/executor.sh",
            cmd="train",
            env=env_vars
        )


@click.command()
@click.option('--dir', help='Set the working directory for your mldock container.', required=True)
@click.option(
    '--params',
    '-p',
    help='(Optional) Hyperparameter override when running container.',
    nargs=2,
    type=click.Tuple([str, str]),
    multiple=True
)
@click.option(
    '--env_vars',
    '-e',
    help='(Optional) Environment Variables override when running container.',
    nargs=2,
    type=click.Tuple([str, str]),
    multiple=True
)
@click.option('--tag', help='docker tag', type=str, default='latest')
@click.option('--port', help='host url at which model is served', type=str, default='8080')
@click.option('--stage', help='environment to stage.')
@click.pass_obj
def deploy(obj, dir, params, env_vars, tag, port, stage):
    """
    Command to deploy ml container on localhost
    """
    verbose = obj.get('verbose', False)
    mldock_manager = MLDockConfigManager(
        filepath=os.path.join(dir, MLDOCK_CONFIG_NAME)
    )
    # get mldock_module_path name
    mldock_config = mldock_manager.get_config()
    module_path = os.path.join(
        dir,
        mldock_config.get("mldock_module_dir", "src"),
    )
    image_name = mldock_config.get("image_name", None)
    container_dir = mldock_config.get("container_dir", None)

    with ProgressLogger(
        group='Stages',
        text='Retrieving Stages',
        spinner='dots',
        on_success='Stages Retrieved'
    ) as spinner:
        stages = mldock_config.get("stages", None)

        if stage is not None:
            tag = stages[stage]['tag']

        if tag is None:
            raise Exception("tag is not valid. Either choose a stage or set a tag manually")

    project_env_vars = mldock_config.get('environment', {})

    for env_var in env_vars:
        key_, value_ = env_var
        print(key_, value_)
        project_env_vars.update(
            {key_: value_}
        )  
    hyperparameters = mldock_config.get('hyperparameters', {})

    # override hyperparameters
    for param in params:
        key_, value_ = param
        print(key_, value_)
        hyperparameters.update(
            {key_: value_}
        )

    env_vars = mldock_utils.collect_mldock_environment_variables(
        stage=stage,
        hyperparameters=mldock_config.get('hyperparameters', {}),
        **project_env_vars
    )

    config_manager = CliConfigureManager()
    env_vars.update(
        config_manager.local.get('environment')
    )

    with ProgressLogger(
        group='Deploy',
        text='Deploying model to {} @ localhost'.format(port),
        spinner='dots'
    ) as spinner:

        spinner.info("Deployment Environment = {}".format(env_vars))
        spinner.start()
        deploy_model(
            working_dir=dir,
            docker_tag=tag,
            image_name=image_name,
            port=port,
            entrypoint="src/container/executor.sh",
            cmd="serve",
            env=env_vars,
            verbose=verbose
        )

@click.command()
def stop():
    """
    Command to stop ml container on localhost
    """

    try:
        containers = search_mldock_containers()

        tags = [
            style_2_level_detail(
                major_detail=c.image.tags[0],
                minor_detail=c.name
             ) for c in containers
        ] + ['abort']
        # newline break
        click.echo("")
        click.secho("Running MLDock containers:", bg='blue', nl=True)
        container_tag = click.prompt(
            text=style_dropdown(group_name="container name", options=tags, default='abort'),
            type=ChoiceWithNumbers(tags, case_sensitive=False),
            show_default=False,
            default='abort',
            show_choices=False
        )
        project_container = None
        for c in containers:
            for image_tag in c.image.tags:
                if image_tag in container_tag:
                    # make newline
                    click.echo("")
                    project_container_tag = click.style(container_tag, fg='bright_blue')
                    if click.confirm(
                        "Stop the running container = {}?".format(
                            project_container_tag) 
                    ):
                        c.kill()

                    break

    except ValueError:
        logger.error("This is not a mldock directory: {}".format(dir))
        raise
    except subprocess.CalledProcessError as exception:
        logger.error(exception)
        raise
    except Exception as exception:
        logger.error(exception)
        raise

local.add_command(build)
local.add_command(predict)
local.add_command(train)
local.add_command(deploy)
local.add_command(stop)
