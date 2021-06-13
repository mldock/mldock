import os
import sys
import logging
import click

from mldock.platform_helpers.docker.auth import login_and_authenticate
from mldock.api.local import \
    docker_build
from mldock.api.registry import \
    push_image_to_repository, pull_image_from_repository
from mldock.config_managers.container import \
    MLDockConfigManager
from mldock.terminal import ProgressLogger, pretty_build_logs

click.disable_unicode_literals_warning = True
logger = logging.getLogger('mldock')
MLDOCK_CONFIG_NAME = 'mldock.json'

def reset_terminal():
    # os.system("clear")
    click.clear()

@click.group()
def registry():
    """
    Commands to interact with docker image registries.
    """
    pass

@click.command()
@click.option(
    '--dir',
    help='Set the working directory for your mldock container.',
    required=True,
    type=click.Path(
        exists=True,
        file_okay=False,
        dir_okay=True,
        writable=True,
        readable=True,
        resolve_path=False,
        allow_dash=False,
        path_type=None
    )
)
@click.option('--no-cache', help='builds container from scratch', is_flag=True)
@click.option(
    '--build',
    help='Set the working directory for your mldock container.',
    is_flag=True
)
@click.option(
    '--provider',
    help='Set the cloud provider',
    required=True,
    type=click.Choice(
        ['ecr', 'gcr', 'dockerhub'],
        case_sensitive=False
    )
)
@click.option(
    '--region',
    help='Set the registry region',
    default=None,
    type=str
)
@click.option('--tag', help='docker tag', type=str, default='latest')
@click.option('--stage', help='environment to stage.')
@click.pass_obj
def push(obj, dir, region, build, provider, no_cache, stage, tag):
    """
    Command to push docker container image to Image Registry
    """
    reset_terminal()
    mldock_manager = MLDockConfigManager(
        filepath=os.path.join(dir, MLDOCK_CONFIG_NAME)
    )
    # get mldock_module_dir name
    mldock_config = mldock_manager.get_config()
    image_name = mldock_config.get("image_name", None)
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
        mldock_config.get("requirements", "requirements.txt")
    )

    # retrieve stages
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

    # athenticate and login docker client
    with ProgressLogger(
        group='Authentication',
        text='Authenticating with {}'.format(provider),
        spinner='dots'
    ) as spinner:
        client, metadata = login_and_authenticate(provider=provider, region=region)
        image_repository = "{}/{}".format(metadata['repository'], image_name)


    if build:
        # build image for cloud repository
        with ProgressLogger(
            group='Build',
            text='Building',
            spinner='dots'
        ) as spinner:
            logs = docker_build(
                image_name=image_repository,
                dockerfile_path=dockerfile_path,
                module_path=module_path,
                target_dir_name=mldock_config.get("mldock_module_dir", "src"),
                requirements_file_path=requirements_file_path,
                no_cache=no_cache,
                docker_tag=tag
            )
            for line in logs:

                spinner.info(pretty_build_logs(line=line))

                spinner.start()

    # Push image to cloud repository
    with ProgressLogger(group='Push', text='Pushing to {}'.format(image_repository), spinner='dots') as spinner:
        states = push_image_to_repository(
            image_repository=image_repository,
            auth_config = {'username': metadata['username'], 'password': metadata['password']},
            tag=tag
        )

        for layer_id, metadata in states.items():

            single_line = "{} {}".format(layer_id, metadata["message"])

            spinner.info(single_line)

        reset_terminal()
        logger.info(obj["logo"])
        spinner.start()

@click.command()
@click.option(
    '--dir',
    help='Set the working directory for your mldock container.',
    required=True,
    type=click.Path(
        exists=True,
        file_okay=False,
        dir_okay=True,
        writable=True,
        readable=True,
        resolve_path=False,
        allow_dash=False,
        path_type=None
    )
)
@click.option('--no-cache', help='builds container from scratch', is_flag=True)
@click.option(
    '--provider',
    help='Set the cloud provider',
    required=True,
    type=click.Choice(['ecr', 'gcr', 'dockerhub'],
    case_sensitive=False
    )
)
@click.option(
    '--region',
    help='Set the registry region',
    default=None,
    type=str
)
@click.option('--tag', help='docker tag', type=str, default='latest')
@click.option('--stage', help='environment to stage.')
@click.pass_obj
def pull(obj, dir, region, provider, no_cache, stage, tag):
    """
    Command to pull docker container image from Image Registry
    """
    mldock_manager = MLDockConfigManager(
        filepath=os.path.join(dir, MLDOCK_CONFIG_NAME)
    )

    # get mldock_module_dir name
    mldock_config = mldock_manager.get_config()
    image_name = mldock_config.get("image_name", None)
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

    # retrieve stages
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

    # login and authenticate
    with ProgressLogger(
        group='Authentication',
        text='Authenticating with {}'.format(provider),
        spinner='dots'
    ) as spinner:
        client, metadata = login_and_authenticate(provider=provider, region=region)
        image_repository = "{}/{}".format(metadata['repository'], image_name)

    # Push image to cloud repository
    with ProgressLogger(
        group='Pull',
        text='Pulling from {}'.format(image_repository),
        spinner='dots'
    ) as spinner:
        states = pull_image_from_repository(
            image_repository=image_repository,
            auth_config = {'username': metadata['username'], 'password': metadata['password']},
            tag=tag
        )

        for layer_id, metadata in states.items():
            single_line = "{} {}".format(layer_id, metadata["message"])

            spinner.info(single_line)

        reset_terminal()
        logger.info(obj["logo"])
        spinner.start()

registry.add_command(push)
registry.add_command(pull)
