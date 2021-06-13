import tests.mocks.aws.boto3 as mock_boto3

from mldock.platform_helpers.aws import auth

class TestAWSDockerAuth:

    def init_mocks(self, mocker):


        mocker.patch(
            'mldock.platform_helpers.aws.auth.boto3',
            mock_boto3
        )

    def test_get_aws_ecr(self, mocker):

        self.init_mocks(mocker)

        username, password, registry, repository = auth.get_aws_ecr(region='eu-west-1')

        assert username == 'USERNAME'

        assert password == 'PASSWORD'

        assert registry == 'ABCXYZ.dkr.ecr.us-west-2.amazonaws.com'

        assert repository == 'ABCXYZ.dkr.ecr.us-west-2.amazonaws.com'
