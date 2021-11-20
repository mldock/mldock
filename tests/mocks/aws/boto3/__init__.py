"""
    AWS Boto3 mock module
"""
from tests.mocks.aws.boto3.ecr import ECR
from tests.mocks.aws.boto3.s3 import S3Resource


def client(service: str, **kwargs):
    """
    Mock of the client function

    args:
        service (str): The Boto3 service requested

    returns:
        service: The Boto3 service class

    """
    services = {"ecr": ECR()}

    return services.get(service)


def resource(resource: str, **kwargs):
    """
    Mock of the client function

    args:
        resource (str): The Boto3 resource requested

    returns:
        resource: The Boto3 resource class

    """
    resources = {"s3": S3Resource()}

    return resources.get(resource)
