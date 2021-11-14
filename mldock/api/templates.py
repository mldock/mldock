"""Container API methods"""

import os
from pathlib import Path
import logging
from github import Github
from environs import Env
from mldock.platform_helpers import utils

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mldock")
env = Env()
env.read_env()  # read .env file, if it exists


def check_available_templates(templates_root, **kwargs):
    """
    initialize mldock container project from template

    args:
        templates_root (str):
    kwargs:
        template_server (str): (default=local) template server to use
    """
    logger.info("Initializing Container Project")

    if kwargs.get("template_server", "local") == "local":
        template_dir = templates_root
        available_templates = [p.name for p in Path(template_dir).iterdir()]
    elif kwargs.get("template_server", "local") == "github":

        # set up in either ENV or configure local
        github_token = env("MLDOCK_GITHUB_TOKEN", default=None)
        github_org = env("MLDOCK_GITHUB_ORG", default="mldock")
        github_repo = env("MLDOCK_GITHUB_REPO", default="mldock-templates")
        github_branch = env("MLDOCK_GITHUB_REPO_BRANCH", default="main")

        github = Github(github_token)

        available_templates = utils.list_templates(
            github, ".", github_org, github_repo, github_branch, root=templates_root
        )

    return available_templates


def init_from_template(template_name, templates_root, src_directory, **kwargs):
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
    logger.info("Initializing Container Project")

    if kwargs.get("template_server", "local") == "local":
        template_dir = templates_root

    elif kwargs.get("template_server", "local") == "github":

        # set up in either ENV or configure local
        github_token = env("MLDOCK_GITHUB_TOKEN", default=None)
        github_org = env("MLDOCK_GITHUB_ORG", default="mldock")
        github_repo = env("MLDOCK_GITHUB_REPO", default="mldock-templates")
        github_branch = env("MLDOCK_GITHUB_REPO_BRANCH", default="main")

        github = Github(github_token)

        template_dir = utils.download_from_git(
            github,
            template_name,
            github_org,
            github_repo,
            github_branch,
            root=templates_root,
        )

    logger.debug("Initializing template based on = {}".format(template_name))
    logger.debug("Template directory = {}".format(template_dir))

    logger.info("Setting up workspace")

    if kwargs.get("container_only", False):
        src_container_directory = os.path.join(src_directory, "container")
        utils._copy_boilerplate_to_dst(
            os.path.join(template_dir, template_name, "src/container"),
            src_container_directory,
            remove_first=True,
        )
    else:
        utils._copy_boilerplate_to_dst(
            os.path.join(template_dir, template_name, "src/"), src_directory
        )

    if kwargs.get("prediction_script", None) is not None:
        new_script_location = Path(src_directory, "prediction.py")
        logger.info(
            f"Copying {kwargs.get('prediction_script', None)} => {new_script_location}"
        )
        utils.copy_file(kwargs.get("prediction_script", None), new_script_location)

    if kwargs.get("trainer_script", None) is not None:
        new_script_location = Path(src_directory, "trainer.py")
        logger.info(
            f"Copying {kwargs.get('trainer_script', None)} => {new_script_location}"
        )
        utils.copy_file(kwargs.get("trainer_script", None), new_script_location)
