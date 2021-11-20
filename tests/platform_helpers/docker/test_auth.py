"""Test dockerhub authentication"""
import pytest

from mldock.platform_helpers.docker import auth
from mldock.platform_helpers.utils import set_env

from tests.mocks import docker as mock_docker
from tests.mocks.aws import boto3 as mock_boto3
from tests.mocks.google.auth import default
from tests.mocks.google.auth import Request


class TestDockerAuth:
    def init_mocks(self, mocker):

        mocker.patch("mldock.platform_helpers.docker.auth.docker", mock_docker)

        mocker.patch("mldock.platform_helpers.aws.auth.boto3", mock_boto3)

        mocker.patch("mldock.platform_helpers.gcp.auth.default", default)

        mocker.patch("mldock.platform_helpers.gcp.auth.Request", Request)

    def testdocker_auth_dockerhub_success(self, mocker):

        self.init_mocks(mocker)

        env_vars = {
            "DOCKERHUB_USERNAME": "USERNAME",
            "DOCKERHUB_PASSWORD": "PASSWORD",
            "DOCKERHUB_REGISTRY": "https://index.docker.io/v1/",
            "DOCKERHUB_REPO": "REPONAME",
        }
        valid_vars = [{"key": key, "value": value} for key, value in env_vars.items()]

        with set_env(**env_vars):

            (client, metadata) = auth.login_and_authenticate(
                provider="dockerhub", region=None
            )

            assert metadata["username"] == "USERNAME"

            assert metadata["password"] == "PASSWORD"

            assert metadata["registry"] == "https://index.docker.io/v1/"

            assert metadata["repository"] == "REPONAME"

    def test_docker_auth_gcr_success(self, mocker):

        self.init_mocks(mocker)

        (client, metadata) = auth.login_and_authenticate(provider="gcr", region="eu")

        assert metadata["username"] == "oauth2accesstoken"

        assert metadata["password"] == "PASSWORD"

        assert metadata["registry"] == "https://eu.gcr.io/myproject"

        assert metadata["repository"] == "eu.gcr.io/myproject"

    def test_docker_auth_ecr_success(self, mocker):

        self.init_mocks(mocker)

        (client, metadata) = auth.login_and_authenticate(provider="ecr", region="eu")

        assert metadata["username"] == "USERNAME"

        assert metadata["password"] == "PASSWORD"

        assert metadata["registry"] == "ABCXYZ.dkr.ecr.us-west-2.amazonaws.com"

        assert metadata["repository"] == "ABCXYZ.dkr.ecr.us-west-2.amazonaws.com"

    def test_docker_auth_not_supported_platform_fail(self, mocker):

        self.init_mocks(mocker)
        provider = "UNKNOWN"
        with pytest.raises(
            TypeError,
            match=r"{PROVIDER} Registry is not implemented.".format(PROVIDER=provider),
        ) as excinfo:
            (client, metadata) = auth.login_and_authenticate(
                provider=provider, region="eu"
            )
