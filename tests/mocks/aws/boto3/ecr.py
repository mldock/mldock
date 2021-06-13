from datetime import datetime
import base64

class ECR:
    """ Mock ECR class
    """

    def get_authorization_token(registryIds: list):

        return {
            'authorizationData': [
                {
                    'authorizationToken': base64.b64encode(s='USERNAME:{}'.format('PASSWORD').encode()),
                    'expiresAt': datetime(2015, 1, 1),
                    'proxyEndpoint': 'ABCXYZ.dkr.ecr.us-west-2.amazonaws.com'
                }
            ]
        }
