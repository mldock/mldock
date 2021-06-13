from tests.mocks.google.auth import default
from tests.mocks.google.auth import Request

from mldock.platform_helpers.gcp import auth

class TestGCPDockerAuth:

    def init_mocks(self, mocker):

        mocker.patch(
            'mldock.platform_helpers.gcp.auth.default',
            default
        )

        mocker.patch(
            'mldock.platform_helpers.gcp.auth.Request',
            Request
        )

    def test_get_gcp_gcr_success(self, mocker):

        self.init_mocks(mocker)

        username, password, registry, repository = auth.get_gcp_gcr(region='eu')

        assert username == 'oauth2accesstoken'

        assert password == 'PASSWORD'

        assert registry == 'https://eu.gcr.io/myproject'

        assert repository == 'eu.gcr.io/myproject'
