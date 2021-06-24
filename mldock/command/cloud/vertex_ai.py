
import os
import sys
import logging
import click
from google.cloud import aiplatform

import json
from pathlib import Path
from future.moves import subprocess

from mldock.platform_helpers.mldock import utils as mldock_utils
from mldock.config_managers.cli import \
    CliConfigureManager
from mldock.terminal import ProgressLogger
from mldock.platform_helpers.mldock import utils as mldock_utils
from mldock.config_managers.container import MLDockConfigManager

click.disable_unicode_literals_warning = True
logger = logging.getLogger('mldock')
MLDOCK_CONFIG_NAME = 'mldock.json'

def reset_terminal():
    # os.system("clear")
    click.clear()

@click.group()
def vertex_ai():
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
    help='(Optional) Hyperparameter override when running container.',
    nargs=2,
    type=click.Tuple([str, str]),
    multiple=True
)
@click.option('--tag', help='docker tag', type=str, default='latest')
@click.option('--stage', help='environment to stage.')
@click.pass_obj
def train(obj, dir, params, env_vars, stage, tag):

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
    platform = mldock_config.get("platform", None)
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

        # compose as key, value
        env_vars_flat = []
        for key, value in env_vars.items():
            env_vars_flat.append({
                'name': key,
                'value': value
            })

    image_name = 'gcr.io/peppy-citron-313311/iris-classifier-py38-cpu'
    project: str = 'peppy-citron-313311'
    display_name: str = image_name

    location: str = "eu-west1"
    api_endpoint: str = "eu-west1-aiplatform.googleapis.com"

    container_image_uri: str = image_name
    # The AI Platform services require regional API endpoints.
    client_options = {"api_endpoint": api_endpoint}
    # Initialize client that will be used to create and send requests.
    # This client only needs to be created once, and can be reused for multiple requests.
    client = aiplatform.gapic.JobServiceClient(client_options=client_options)

    custom_job = {
        "display_name": display_name,
        "job_spec": {
            "worker_pool_specs": [
                {
                    "machine_spec": {
                        "machine_type": "n1-standard-4",
                        # "accelerator_type": aiplatform.gapic.AcceleratorType.NVIDIA_TESLA_K80,
                        # "accelerator_count": 1,
                    },
                    "replica_count": 1,
                    "container_spec": {
                        "image_uri": container_image_uri,
                        "command": ['train'],
                        "args": [],
                        "env": env_vars_flat
                    },
                }
            ]
        },
    }
    parent = f"projects/{project}/locations/{location}"
    response = client.create_custom_job(parent=parent, custom_job=custom_job)
    print("response:", response)

vertex_ai.add_command(train)
