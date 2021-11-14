"""
    AWS Auth utilities
"""
import base64
import boto3

from mldock.platform_helpers.utils import strip_scheme


def get_aws_ecr(region: str):
    """
    Get Authentication credentials for AWS ECR using boto3

    args:
        region (str): AWS region of the registry to authenticate

    return:
        username (str): username to use in docker client auth
        password (str): password token to use in docker client auth
        registry (str): registry url to use
    """
    # this loads AWS access token and secret from env and returns an ECR client
    ecr_client = boto3.client("ecr", region_name=region)

    # get login token
    token = ecr_client.get_authorization_token()

    username, password = (
        base64.b64decode(token["authorizationData"][0]["authorizationToken"])
        .decode()
        .split(":")
    )

    registry = token["authorizationData"][0]["proxyEndpoint"]

    cloud_repository = strip_scheme(registry)
    # return docker credentials
    return username, password, registry, cloud_repository
