
class Credentials(object):

    @staticmethod
    def refresh(request, **kwargs):

        pass

    @property
    def token(self):
        return 'PASSWORD'

def default(scopes: list, **kwargs):
    return Credentials(), 'myproject'

class Request(object):
    pass
