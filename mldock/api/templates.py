"""Container API methods"""

import os
import sys
from pathlib import Path
import logging
from github import Github
from environs import Env
from mldock.platform_helpers import utils

logger = logging.getLogger('mldock')
env = Env()
env.read_env()  # read .env file, if it exists


def init_from_template(template_name, templates_root, src_directory, container_only: bool = False, template_server='local'):

    logger.info("Initializing Container Project")

    if template_server == 'local':
        template_dir = templates_root

    elif template_server == 'github':

        # set up in either ENV or configure local
        GITHUB_TOKEN = env("MLDOCK_GITHUB_TOKEN", default=None)
        org = env("MLDOCK_GITHUB_ORG", default=None)
        repo = env("MLDOCK_GITHUB_REPO", default=None)
        branch = env("MLDOCK_GITHUB_REPO_BRANCH", default=None)

        if GITHUB_TOKEN is None:
            raise KeyError(
                "Template server == 'github' requires the "
                "following environment variables: "
                "MLDOCK_GITHUB_TOKEN, MLDOCK_GITHUB_ORG, "
                "MLDOCK_GITHUB_REPO, MLDOCK_GITHUB_REPO_BRANCH"
            )

        github = Github(GITHUB_TOKEN)
        template_dir = utils.download_from_git(github, template_name, org, repo, branch, root=templates_root)

    logger.debug("Initializing template based on = {}".format(template_name))
    logger.debug("Template directory = {}".format(template_dir))

    logger.info("Setting up workspace") 

    if container_only:
        src_container_directory = os.path.join(
            src_directory,
            'container'
        )
        utils._copy_boilerplate_to_dst(
            os.path.join(template_dir, template_name, 'src/container'),
            src_container_directory,
            remove_first=True
        )
    else:
        utils._copy_boilerplate_to_dst(
            os.path.join(template_dir, template_name, 'src/'),
            src_directory
        )
