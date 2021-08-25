"""Container API methods"""

import os
from pathlib import Path
import logging
from github import Github
from environs import Env
from mldock.platform_helpers import utils

logger = logging.getLogger('mldock')
env = Env()
env.read_env()  # read .env file, if it exists


def init_from_template(
    template_name,
    templates_root,
    src_directory,
    **kwargs
):
    """
        initialize mldock container project from template

        args:
            template_name (str):
            templates_root (str):
            src_directory (str):
            container_only (bool): (default=False) only initialize the container directory
            template_server (str): (default=local) template server to use
        kwargs:
            container_only (bool): (default=False) only initialize the container directory
            template_server (str): (default=local) template server to use
            prediction_script (str): (default=None) optional prediction script to use
            trainer_script (str): (default=None) optional trainer script to use
    """
    container_only = kwargs.get('container_only', False)
    template_server = kwargs.get('template_server', 'local')
    prediction_script = kwargs.get('prediction_script', None)
    trainer_script = kwargs.get('trainer_script', None)

    logger.info("Initializing Container Project")

    if template_server == 'local':
        template_dir = templates_root

    elif template_server == 'github':

        # set up in either ENV or configure local
        github_token = env("MLDOCK_GITHUB_TOKEN", default=None)
        github_org = env("MLDOCK_GITHUB_ORG", default=None)
        github_repo = env("MLDOCK_GITHUB_REPO", default=None)
        github_branch = env("MLDOCK_GITHUB_REPO_BRANCH", default=None)

        if github_token is None:
            raise KeyError(
                "Template server == 'github' requires the "
                "following environment variables: "
                "MLDOCK_GITHUB_TOKEN, MLDOCK_GITHUB_ORG, "
                "MLDOCK_GITHUB_REPO, MLDOCK_GITHUB_REPO_BRANCH"
            )

        github = Github(github_token)
        template_dir = utils.download_from_git(
            github,
            template_name,
            github_org,
            github_repo,
            github_branch,
            root=templates_root
        )

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

    if prediction_script is not None:
        new_script_location = Path(src_directory, 'prediction.py')
        logger.info(f"Copying {prediction_script} => {new_script_location}")
        utils.copy_file(
            prediction_script,
            new_script_location
        )

    if trainer_script is not None:
        new_script_location = Path(src_directory, 'trainer.py')
        logger.info(f"Copying {trainer_script} => {new_script_location}")
        utils.copy_file(
            trainer_script,
            new_script_location
        )
