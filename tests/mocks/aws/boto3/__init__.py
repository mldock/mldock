"""
    AWS Boto3 mock module
"""
from tests.mocks.aws.boto3.ecr import ECR


def client(service: str, **kwargs):
    """
        Mock of the client function

        args:
            service (str): The Boto3 service requested

        returns:
            service: The Boto3 service class

    """
    services = {
        'ecr': ECR()
    }

    return services.get(service)