class Client:
    """docker client mock"""

    @staticmethod
    def login(
        username: str, password: str, email: str, registry: str, reauth: bool, **kwargs
    ):
        return {
            "username": "USERNAME",
            "password": "PASSWORD",
            "registry": "https://index.docker.io/v1/",
            "repository": "REPONAME",
        }


def from_env():

    return Client()
