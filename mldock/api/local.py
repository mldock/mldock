"""Local API methods"""
import os
import logging
from pathlib import Path
import requests
import docker

from mldock.config_managers.cli import CliConfigureManager
from mldock.platform_helpers import utils

logger = logging.getLogger("mldock")

# log formatting
def pretty_build_logs(line: dict):
    """format docker build logs"""
    if line is None:
        return None

    error = line.get("error", None)
    error_detail = line.get("errorDetail", None)

    if error is not None:
        logger.error("{}\n{}".format(error, error_detail))

    stream = line.get("stream", "")

    if ("Step" in stream) & (":" in stream):
        logger.info(" ==> {MESSAGE}".format(MESSAGE=stream))
    else:
        logger.debug(" ==> {MESSAGE}".format(MESSAGE=stream))

    return None


class DockerLLCManager:
    """Docker APIClient context manager"""

    client = None

    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def __enter__(self):
        self.client = docker.APIClient(**self.kwargs)
        return self.client

    def __exit__(self, exc_type, exc_value, exc_tb):
        logger.info(self.client.prune_builds())
        self.client.close()


class DockerManager:
    """Docker Client context manager"""

    client = None

    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def __enter__(self):
        self.client = docker.from_env(**self.kwargs)
        return self.client

    def __exit__(self, exc_type, exc_value, exc_tb):
        self.client.close()


# API methods


def generate_mldock_mount_volume(
    host_prefix: str,
    container_prefix: str,
    working_dir: str,
    base_container_path: str,
    mode: str = "rw",
):
    """
    generate host and container paths for docker volume mounts.

    args:
        host_prefix (str): host prefix to use relative to working_dir
        container_prefix (str): container prefix to use relative to base_container_path
        working_dir (str): host working directory to build host volumes from
        base_container_path (str): container base path to build container volumes from
        mode (str): (default='rw') docker volume mount read/write mode
    """
    host_path = Path(working_dir, host_prefix).absolute().as_posix()
    container_path = Path(base_container_path, container_prefix).as_posix()
    return host_path, {"bind": container_path, "mode": mode}


def make_multiple_mldock_mount_volumes(
    volumes: dict, working_dir: str, base_container_path: str, mode: str = "rw"
):
    """
    Generate multiple docker volume mounts for a collection of volume mount mappings.

    args:
        volumes (dict): volume mount mappings
        working_dir (str): host working directory to build host volumes from
        base_container_path (str): container base path to build container volumes from
        mode (str): (default='rw') docker volume mount read/write mode
    """
    docker_volumes = {}
    for volume in volumes:

        host_mount, container_mount = generate_mldock_mount_volume(
            host_prefix=volume["host_prefix"],
            container_prefix=volume["container_prefix"],
            working_dir=working_dir,
            base_container_path=base_container_path,
            mode=mode,
        )

        docker_volumes.update({host_mount: container_mount})
    return docker_volumes


def train_model(working_dir, docker_tag, image_name, entrypoint, **kwargs):
    """
    Trains ML model(s) locally
    :param working_dir: [str], source root directory
    :param docker_tag: [str], the Docker tag for the image
    :param image_name: [str], The name of the Docker image
    """

    config_manager = CliConfigureManager()

    try:
        with DockerManager() as client:
            base_ml_path = kwargs.get("base_ml_path", "/opt/ml")

            container_volumes = make_multiple_mldock_mount_volumes(
                volumes=[
                    {"host_prefix": "config", "container_prefix": "input/config"},
                    {"host_prefix": "data", "container_prefix": "input/data"},
                    {"host_prefix": "model", "container_prefix": "model"},
                    {"host_prefix": "output", "container_prefix": "output"},
                ],
                working_dir=working_dir,
                base_container_path=base_ml_path,
                mode="rw",
            )

            if config_manager.local.get("auth_type", None) is not None:

                credentials_volume = utils.get_sdk_credentials_volume_mount(
                    config_manager.local.get("auth_type")
                )

                container_volumes.update(credentials_volume)

            container = client.containers.run(
                image="{IMAGE}:{TAG}".format(IMAGE=image_name, TAG=docker_tag),
                entrypoint=entrypoint,
                command=kwargs.get("cmd", "train"),
                environment=kwargs.get("env", {}),
                remove=True,
                tty=True,
                volumes=container_volumes,
                detach=True,
                stream=True,
            )
            logs = container.logs(follow=True).decode("utf-8")

            logger.info(logs)
    except (KeyboardInterrupt, SystemExit) as exception:
        logger.error(exception)
        container.kill()
        raise
    except (
        docker.errors.APIError,
        docker.errors.ContainerError,
        docker.errors.ImageNotFound,
    ) as exception:
        logger.error(exception)
        raise
    except Exception as exception:
        logger.error(exception)
        raise


def deploy_model(working_dir, docker_tag, image_name, entrypoint, **kwargs):
    """
    Deploys ML models(s) locally
    :param working_dir: [str], source root directory
    :param docker_tag: [str], the Docker tag for the image
    :param image_name: [str], The name of the Docker image
    """

    config_manager = CliConfigureManager()
    try:
        with DockerManager() as client:
            base_ml_path = kwargs.get("base_ml_path", "/opt/ml")

            container_volumes = make_multiple_mldock_mount_volumes(
                volumes=[
                    {"host_prefix": "config", "container_prefix": "input/config"},
                    {"host_prefix": "data", "container_prefix": "input/data"},
                    {"host_prefix": "model", "container_prefix": "model"},
                    {"host_prefix": "output", "container_prefix": "output"},
                ],
                working_dir=working_dir,
                base_container_path=base_ml_path,
                mode="rw",
            )

            if config_manager.local.get("auth_type", None) is not None:

                credentials_volume = utils.get_sdk_credentials_volume_mount(
                    config_manager.local.get("auth_type")
                )

                container_volumes.update(credentials_volume)

            container = client.containers.run(
                image="{IMAGE}:{TAG}".format(IMAGE=image_name, TAG=docker_tag),
                entrypoint=entrypoint,
                command=kwargs.get("cmd", "serve"),
                environment=kwargs.get("env", {}),
                ports=kwargs.get("port", {8080: 8080}),
                remove=True,
                tty=True,
                volumes=container_volumes,
                auto_remove=True,
                detach=True,
                stream=True,
            )

            if kwargs.get("verbose", False):
                logs = container.logs(follow=True).decode("utf-8")

                logger.info(logs)

    except requests.exceptions.ConnectionError as exception:
        logger.info(
            "\nWorker socket connection timed out. "
            "\n\nThis can happen when connection pool is overloaded. "
            "We suggest setting environment variable: "
            "DOCKER_CLIENT_TIMEOUT=120 to give the client more time."
        )

    except (KeyboardInterrupt, SystemExit) as exception:
        logger.error(exception)
        container.kill()
        raise
    except (
        docker.errors.APIError,
        docker.errors.ContainerError,
        docker.errors.ImageNotFound,
    ) as exception:
        logger.error(exception)
        raise
    except Exception as exception:
        logger.error(exception)
        raise


def docker_build(
    image_name: str,
    dockerfile_path: str,
    module_path: str,
    requirements_file_path: str,
    **kwargs
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
            base_url=os.environ.get("DOCKER_HOST", "unix:///var/run/docker.sock"),
        ) as client:

            full_image_name = "{IMAGE}:{TAG}".format(
                IMAGE=image_name, TAG=kwargs.get("docker_tag", "latest")
            )
            logs = client.build(
                tag=full_image_name,
                path=".",
                dockerfile=Path(dockerfile_path).as_posix(),
                buildargs={
                    "module_path": Path(module_path).as_posix(),
                    "target_dir_name": Path(
                        kwargs.get("target_dir_name", "src")
                    ).as_posix(),
                    "requirements_file_path": Path(requirements_file_path).as_posix(),
                    "container_platform": kwargs.get("container_platform", None),
                },
                nocache=kwargs.get("no_cache", False),
                rm=True,
                decode=True,
            )
            for line in logs:
                yield line

    except (KeyboardInterrupt, SystemExit) as exception:
        logger.error(exception)
        raise
    except (
        docker.errors.APIError,
        docker.errors.ContainerError,
        docker.errors.ImageNotFound,
    ) as exception:
        logger.error(exception)
        raise
    except (docker.errors.DockerException) as exception:
        if "NewConnectionError" in str(exception):
            raise Exception(
                (
                    "Unable to connect to docker daemon. "
                    "Set environment variable: DOCKER_HOST"
                )
            ) from exception
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
        mldock_filters.update({"ancestor": ancestor})

    label = kwargs.get("label", ["MLDOCK__IS_MLDOCK_CONTAINER=true"])
    mldock_filters.update({"label": label})
    containers = client.containers.list(filters=mldock_filters)

    return containers
