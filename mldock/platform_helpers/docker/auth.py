"""
    Docker Auth Utilities aand workflows
"""
import os
import logging
from urllib.parse import urlparse
import docker

from mldock.platform_helpers.aws.auth import get_aws_ecr
from mldock.platform_helpers.gcp.auth import get_gcp_gcr
from mldock.platform_helpers.dockerhub.auth import get_dockerhub_credentials

logger = logging.getLogger('mldock')

def login_and_authenticate(provider: str, region: str):
    """
    Login and authenticate with registry

    DockerHub - https://ropenscilabs.github.io/r-docker-tutorial/04-Dockerhub.html
    AWS - https://aws.amazon.com/blogs/compute/authenticating-amazon-ecr-repositories-for-docker-cli-with-credential-helper/
    GCP - https://cloud.google.com/artifact-registry/docs/docker/authentication
    Azure - https://docs.microsoft.com/en-us/azure/container-registry/container-registry-repository-scoped-permissions
    """
    client = docker.from_env()

    if provider == 'ecr':
        # AWS ECR
        username, password, registry, repo = get_aws_ecr(region=region)
    elif provider == 'gcr':
        # GCP 
        username, password, registry, repo = get_gcp_gcr(region=region)
    elif provider == 'dockerhub':
        # DockerHub
        username, password, registry, repo = get_dockerhub_credentials()
    else:
        raise TypeError("{PROVIDER} Registry is not implemented.".format(PROVIDER=provider))

    # login
    response = client.login(
        username=username,
        password=password,
        email=None,
        registry=registry,
        reauth=True
    )

    # return logged in client
    return client, {
        'username': username,
        'password': password,
        'registry': registry,
        'repository': repo
    }
