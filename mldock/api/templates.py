"""Container API methods"""

import os
import sys
from pathlib import Path
import tempfile
import base64
import logging
from github import Github
from github import GithubException
from github.GithubException import UnknownObjectException
from environs import Env

from mldock.platform_helpers import utils


env = Env()
env.read_env()  # read .env file, if it exists
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('mldock')
GITHUB_TOKEN = env("MLDOCK_GITHUB_TOKEN")
github = Github(GITHUB_TOKEN)

def get_sha_for_tag(repository, tag):
    """
    Returns a commit PyGithub object for the specified repository and tag.
    """
    branches = repository.get_branches()
    matched_branches = [match for match in branches if match.name == tag]
    if matched_branches:
        return matched_branches[0].commit.sha

    tags = repository.get_tags()
    matched_tags = [match for match in tags if match.name == tag]
    if not matched_tags:
        raise ValueError('No Tag or Branch exists with that name')
    return matched_tags[0].commit.sha

def download_directory(repository, sha, server_path, local_prefix, relative_to):
    """
    Download all contents at server_path with commit tag sha in
    the repository.
    """
    try:
        contents = repository.get_contents(server_path, ref=sha)

        for content in contents:
            logger.info("Downloading {}".format(content.path))
            local_path = Path(local_prefix, Path(content.path).relative_to(relative_to))
            if content.type == 'dir':
                local_path.mkdir(parents=True, exist_ok=True)
                download_directory(
                    repository=repository,
                    sha=sha,
                    server_path=content.path,
                    local_prefix=local_prefix,
                    relative_to=relative_to
                )
            else:
                file_content = repository.get_contents(content.path, ref=sha)
                file_data = base64.b64decode(file_content.content)

                # set executables with chmod +x
                # given that mldock containers always have the "executor.sh"
                if local_path.name == 'executor.sh':
                    local_path.touch(0o777)
                else:
                    local_path.touch()

                with open(local_path, "w+") as file_out:
                    file_out.write(file_data.decode())
                    file_out.write("\n")
    except (GithubException, IOError) as exc:

        # get exc info
        exc_type, exc_value, exc_traceback = sys.exc_info()

        # if Unknown Object, inform user path is missing.
        if exc_type == UnknownObjectException:
            new_error = (
                "Server path = '{SERVER_PATH}' was "
                "not found in repository = '{REPOSITORY_NAME}'.".format(
                    SERVER_PATH=server_path,
                    REPOSITORY_NAME=repository.name
                )
            )
            logger.error(new_error)
            sys.exit(-1)
        raise

def download_from_git(start_dir, org, repo, branch, root: str = '.'):
    """Download the server path from git remote directory"""
    organization = github.get_organization(org)
    repository = organization.get_repo(repo)
    sha = get_sha_for_tag(repository, branch)

    tmp_dir = tempfile.mkdtemp()
    ## download to tmp
    download_directory(
        repository,
        sha,
        server_path=Path(root, start_dir).as_posix(),
        local_prefix=tmp_dir,
        relative_to=root
    )

    return tmp_dir


def init_from_template(template_name, templates_root, src_directory, container_only: bool = False, template_server='local'):

    logger.info("Initializing Container Project")

    if template_server == 'local':
        template_dir = templates_root

    elif template_server == 'github':

        # set up in either ENV or configure local
        org = env("MLDOCK_GITHUB_ORG")
        repo = env("MLDOCK_GITHUB_REPO")
        branch = env("MLDOCK_GITHUB_REPO_BRANCH")
        template_dir = download_from_git(template_name, org, repo, branch, root=templates_root)

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
