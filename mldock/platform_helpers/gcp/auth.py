"""
    GCP Auth utilities
"""
import os
from google.auth import default
from google.auth.transport.requests import Request

from mldock.platform_helpers.utils import strip_scheme

def get_gcp_gcr(region: str):
    """
        Get Authentication credentials for google.auth

        args:
            region (str): Region to Authenticate GCR registry in
        
        return:
            username (str): username to use in docker client auth
            password (str): password token to use in docker client auth
            registry (str): registry url to use
    """
    credentials, project = default(
        scopes=['https://www.googleapis.com/auth/cloud-platform']
    )
    # creds.valid is False, and creds.token is None
    # Need to refresh credentials to populate those
    auth_req = Request()
    credentials.refresh(auth_req)
    # set docker creds
    username = 'oauth2accesstoken'
    password = credentials.token
    if region == 'eu':
        registry = 'https://eu.gcr.io'
    elif region == 'us':
        registry = 'https://us.gcr.io'
    elif region == 'asia':
        registry = 'https://asia.gcr.io'
    else:
        registry = 'https://gcr.io'

    registry = os.path.join(registry, project)
    # return docker credentials
    cloud_repository = strip_scheme(registry)
    # return docker credentials
    return username, password, registry, cloud_repository
