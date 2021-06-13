"""Authenticate docker to dockerhub"""
from environs import Env

def get_dockerhub_credentials():
    """
        Get Authentication credentials for Dockerhub

        return:
            username (str): username to use in docker client auth
            password (str): password token to use in docker client auth
            registry (str): registry url to use
    """
    # pick up from environment otherwise raise error
    env = Env()
    env.read_env()

    username = env("DOCKERHUB_USERNAME")
    password = env("DOCKERHUB_PASSWORD")
    registry = env("DOCKERHUB_REGISTRY")
    repo = env("DOCKERHUB_REPO")
    # return docker credentials
    return username, password, registry, repo
