import os
import sys
import logging
import click
import sagemaker
from sagemaker.estimator import Estimator
from sagemaker.serializers import JSONSerializer
from sagemaker.deserializers import JSONDeserializer

from mldock.platform_helpers.docker.auth import login_and_authenticate
from mldock.api.local import \
    docker_build, DockerManager
from mldock.api.registry import \
    push_image_to_repository, pull_image_from_repository
from mldock.platform_helpers.mldock import utils as mldock_utils
from mldock.config_managers.container import \
    MLDockConfigManager
from mldock.config_managers.cli import \
    CliConfigureManager
from mldock.terminal import ProgressLogger

click.disable_unicode_literals_warning = True
logger = logging.getLogger('mldock')
MLDOCK_CONFIG_NAME = 'mldock.json'

def reset_terminal():
    # os.system("clear")
    click.clear()

@click.group()
def sagemaker():
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
@click.option('--payload', default=None, help='payload file name', required=True)
@click.option('--content-type', default='json', help='format of payload', type=click.Choice(['json', 'csv'], case_sensitive=False))
@click.option('--host', help='host url at which model is served', type=str, default='http://127.0.0.1:8080/invocations')
@click.option('--tag', help='docker tag', type=str, default='latest')
@click.option('--stage', help='environment to stage.')
@click.pass_obj
def smoke_test(obj, dir, payload, content_type, host, params, env_vars, stage, tag):
    """
        Run smoke test for sagemaker

        Runs local training job and deploys model locally, finally passing it your payload
        for testing.

        note: Due to sagemakers tightly coupled apis in local mode it is not possible to
        deploy a local testing endpoint without first running a training step.
        Other methods like creating a model and then deploying are also quite involved due to the
        complex coupling of different API's like session and environment.
    """
    mldock_manager = MLDockConfigManager(
        filepath=os.path.join(dir, MLDOCK_CONFIG_NAME)
    )
    # get mldock_module_dir name
    mldock_config = mldock_manager.get_config()
    image_name = mldock_config.get("image_name", None)
    data = mldock_config.get("data", None)
    payload = os.path.join(dir, payload)

    # flatten data node
    data_flat = {}
    for data_node in data:
        data_path = os.path.join('file://', dir, 'data', data_node['channel'], data_node['filename'])

        data_flat.update({
            data_node['channel']: data_path
        })

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
        group='Smoketest-Training',
        text='Retrieving Training Cloud Smoketest',
        spinner='dots'
    ) as spinner:
        estimator = Estimator(
            image_uri=image_name,
            role="arn:aws:iam::013389100338:role/service-role/AmazonSageMaker-ExecutionRole-20200317T111790",
            instance_count=1,
            instance_type="local",
            environment=env_vars
        )

        estimator.fit(data_flat)

    reset_terminal()
    with ProgressLogger(
        group='Smoketest-Deploy',
        text='Retrieving Deploying Cloud Smoketest',
        spinner='dots'
    ) as spinner:
        predictor = estimator.deploy(
            initial_instance_count=1,
            instance_type='local',
            serializer=JSONSerializer(),
            deserializer=JSONDeserializer(),
            wait=False
        )

    reset_terminal()

    with ProgressLogger(
        group='Smoketest-Predict',
        text='Running Smoketest Prediction Request',
        spinner='dots'
    ) as spinner:
        spinner.clear()
        spinner.start()
        if payload is None:
            logger.info("\nPayload cannot be None. Please provide path to payload file.")
        else:
            if content_type in ['application/json', 'json']:
                pretty_output = predictor.predict(
                    data=payload
                )
            elif content_type in ['text/csv', 'csv']:
                pretty_output = predictor.predict(
                    data=payload
                )
            else:
                raise Exception("Content-type is not supported.")
            logger.info(pretty_output)

    reset_terminal()
    with ProgressLogger(
        group='Smoketest-CleanUp',
        text='Cleaning Up Cloud Smoketest',
        spinner='dots'
    ) as spinner:
        # delete endpoint
        predictor.delete_endpoint(delete_endpoint_config=True)
        with DockerManager() as client:
            client.containers.prune()

sagemaker.add_command(smoke_test)
