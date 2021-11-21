"""Test dockerhub authentication"""
from mldock.platform_helpers.dockerhub import auth
from mldock.platform_helpers import utils


class TestDockerhubAuth:
    def test_get_dockerhub_credentials_success(self):

        env_vars = {
            "DOCKERHUB_USERNAME": "USERNAME",
            "DOCKERHUB_PASSWORD": "PASSWORD",
            "DOCKERHUB_REGISTRY": "https://index.docker.io/v1/",
            "DOCKERHUB_REPO": "REPONAME",
        }
        valid_vars = [{"key": key, "value": value} for key, value in env_vars.items()]

        with utils.set_env(**env_vars):

            username, password, registry, repository = auth.get_dockerhub_credentials()

            assert username == "USERNAME"

            assert password == "PASSWORD"

            assert registry == "https://index.docker.io/v1/"

            assert repository == "REPONAME"
