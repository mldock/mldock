"""Local API methods"""
import os
import sys
import json
import logging
from pathlib import Path
import docker
import traceback
import logging


from mldock.config_managers.cli import \
    CliConfigureManager
from mldock.platform_helpers import utils

logger=logging.getLogger('mldock')

# log formatting
def pretty_build_logs(line: dict):

    if line is None:
        return None

    error = line.get('error', None)
    errorDetail = line.get('errorDetail', None)

    if error is not None:
        logger.error('{}\n{}'.format(error, errorDetail))
    
    stream = line.get('stream', '')

    if ('Step' in stream) & (':' in stream):
        logger.info(" ==> {MESSAGE}".format(MESSAGE=stream))
    else:
        logger.debug(" ==> {MESSAGE}".format(MESSAGE=stream))


class DockerLLCManager:

    def __init__(self, **kwargs):
        self.kwargs = kwargs 
    def __enter__(self):
        self.client = docker.APIClient(**self.kwargs)
        return self.client
    def __exit__(self, exc_type, exc_value, exc_tb):
        logger.info(self.client.prune_builds())
        self.client.close()

class DockerManager:

    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def __enter__(self):
        self.client = docker.from_env(**self.kwargs)
        return self.client
    def __exit__(self, exc_type, exc_value, exc_tb):
        self.client.close()

# API methods

def train_model(working_dir, docker_tag, image_name, entrypoint, cmd, env=None):
    """
    Trains ML model(s) locally
    :param working_dir: [str], source root directory
    :param docker_tag: [str], the Docker tag for the image
    :param image_name: [str], The name of the Docker image
    """
    process_env = {}
    if env is not None:
        process_env.update(env)

    config_manager = CliConfigureManager()

    try:
        with DockerManager() as client:
            base_ml_path = '/opt/ml'

            container_volumes = {
                Path(working_dir,'config').absolute().as_posix(): {'bind': Path(base_ml_path,'input/config').as_posix(), 'mode': 'rw'},
                Path(working_dir,'data').absolute().as_posix(): {'bind': Path(base_ml_path,'input/data').as_posix(), 'mode': 'rw'},
                Path(working_dir,'model').absolute().as_posix(): {'bind': Path(base_ml_path,'model').as_posix(), 'mode': 'rw'},
                Path(working_dir,'output').absolute().as_posix(): {'bind': Path(base_ml_path,'output').as_posix(), 'mode': 'rw'}
            }

            if config_manager.local.get('auth_type', None) is not None:

                credentials_volume = utils.get_sdk_credentials_volume_mount(config_manager.local.get('auth_type'))
                container_volumes.update(credentials_volume)

            container = client.containers.run(
                image="{IMAGE}:{TAG}".format(IMAGE=image_name, TAG=docker_tag),
                entrypoint=entrypoint,
                command=cmd,
                environment=process_env,
                remove=True,
                tty=True,
                volumes=container_volumes,
                detach=True,
                stream=True
            )
            logs = container.logs(follow=True).decode('utf-8')

            logger.info(logs)
    except (KeyboardInterrupt, SystemExit) as exception:
        logger.error(exception)
        container.kill()
        raise
    except (docker.errors.APIError, docker.errors.ContainerError, docker.errors.ImageNotFound) as exception:
        logger.error(exception)
        raise
    except Exception as exception:
        logger.error(exception)
        raise

def deploy_model(working_dir, docker_tag, image_name, entrypoint, cmd, port=8080, env={}):
    """
    Deploys ML models(s) locally
    :param working_dir: [str], source root directory
    :param docker_tag: [str], the Docker tag for the image
    :param image_name: [str], The name of the Docker image
    """

    process_env = {}
    if isinstance(env, dict) and len(env) > 0:
        process_env.update(env)

    config_manager = CliConfigureManager()
    try:
        with DockerManager() as client:
            base_ml_path = '/opt/ml'
            container_volumes = {
                Path(working_dir,'config').absolute().as_posix(): {'bind': Path(base_ml_path,'input/config').as_posix(), 'mode': 'rw'},
                Path(working_dir,'data').absolute().as_posix(): {'bind': Path(base_ml_path,'input/data').as_posix(), 'mode': 'rw'},
                Path(working_dir,'model').absolute().as_posix(): {'bind': Path(base_ml_path,'model').as_posix(), 'mode': 'rw'},
                Path(working_dir,'output').absolute().as_posix(): {'bind': Path(base_ml_path,'output').as_posix(), 'mode': 'rw'}
            }

            if config_manager.local.get('auth_type', None) is not None:

                credentials_volume = utils.get_sdk_credentials_volume_mount(config_manager.local.get('auth_type'))
                container_volumes.update(credentials_volume)

            container = client.containers.run(
                image="{IMAGE}:{TAG}".format(IMAGE=image_name, TAG=docker_tag),
                entrypoint=entrypoint,
                command=cmd,
                environment=process_env,
                ports={8080: port},
                remove=True,
                tty=True,
                volumes=container_volumes,
                auto_remove=True,
                detach=True,
                stream=True
            )

    except (KeyboardInterrupt, SystemExit) as exception:
        logger.error(exception)
        container.kill()
        raise
    except (docker.errors.APIError, docker.errors.ContainerError, docker.errors.ImageNotFound) as exception:
        logger.error(exception)
        raise
    except Exception as exception:
        logger.error(exception)
        raise

def docker_build(
    image_name: str,
    dockerfile_path: str,
    module_path: str,
    target_dir_name: str,
    requirements_file_path: str,
    no_cache: bool,
    docker_tag: str,
    container_platform: str = None
):
    """Runs the build executable using docker python sdk.

    Args:
        script_path (str): relative path to script when run on root
        base_path (str):
        image_name (str):
        dockerfile_path (str):
        module_path (str):
        target_dir_name (str):
        requirements_file_path (str):
        docker_tag (str): the docker tag to build
    """
    try:

        with DockerLLCManager(
            max_pool_size=20,
            base_url=os.environ.get('DOCKER_HOST','unix:///var/run/docker.sock')
        ) as client:

            logs = client.build(
                tag="{IMAGE}:{TAG}".format(IMAGE=image_name, TAG=docker_tag),
                path='.',
                dockerfile=Path(os.path.join(dockerfile_path, 'Dockerfile')).as_posix(),
                buildargs={
                    'module_path': Path(module_path).as_posix(),
                    'target_dir_name': Path(target_dir_name).as_posix(),
                    'requirements_file_path': Path(requirements_file_path).as_posix(),
                    'container_platform': container_platform
                },
                nocache=no_cache,
                rm=True,
                decode=True
            )
            for line in logs:
                yield line
            #     pretty_build_logs(line=line)

    except (KeyboardInterrupt, SystemExit) as exception:
        logger.error(exception)
        raise
    except (docker.errors.DockerException) as exception:
        if "NewConnectionError" in str(exception):
            raise Exception("Unable to connect to docker daemon. Set environment variable: DOCKER_HOST")
        raise
    except (docker.errors.APIError, docker.errors.ContainerError, docker.errors.ImageNotFound) as exception:
        logger.error(exception)
        raise
    except Exception as exception:
        logger.error(exception)
        raise

def search_mldock_containers(**kwargs):
    """Performs a docker ps with filters. Incorporating the label to find only MLDOCK Containers"""
    mldock_filters = {}
    client = docker.from_env()
    ancestor = kwargs.get("ancestor", None)
    if ancestor is not None:
        mldock_filters.update({
            "ancestor": ancestor
        })
    
    label = kwargs.get("label", ["MLDOCK__IS_MLDOCK_CONTAINER=true"])
    mldock_filters.update(
        {
            "label": label
        }
    )
    containers = client.containers.list(filters=mldock_filters)

    return containers
