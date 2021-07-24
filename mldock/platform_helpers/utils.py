"""PLATFORM HELPER UTILITIES"""
import sys
import os
import contextlib
import json
from urllib.parse import urlparse
from pathlib import Path
import tarfile
import zipfile
from typing import Iterator
import logging
import re
from distutils.dir_util import copy_tree, remove_tree
from distutils.dir_util import mkpath
from distutils.file_util import write_file
import tempfile
import base64

from github import GithubException
from github.GithubException import UnknownObjectException

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('mldock')

def _mkdir(dir_path: str):
    """make directory structure

    Args:
        dir_path (str): directory path to build
    """
    Path(dir_path).mkdir(parents=True, exist_ok=True)

def _iter_nested_dir(root_dir: str) -> Iterator[str]:
    """Iterate through nested folders.

    Args:
        root_dir (str): name of the directory to start form

    Yields:
        Iterator[str]: path iterator
    """
    rootdir = Path(root_dir)
    for path in rootdir.glob('**/*'):
        yield path

def _delete_file(file_path):
    """Delete a file

    Args:
        file_path (str): path to file

    Raises:
        TypeError: Expected a file_path of type file. Cannot be directory or other.
    """
    path = Path(file_path)
    if not path.is_file():
        raise TypeError("Expected a file_path of type file. Only deletes files")

    os.remove(path)

def _check_if_cloud_scheme(url: str, scheme: str = 's3') -> bool:
    parsed_url = urlparse(url)
    return parsed_url.scheme == scheme

def parse_url(url: str, scheme: str = 's3'):
    """Returns an (s3 bucket, key name/prefix) tuple from a url with an s3
    scheme.
    Args:
        url (str):
    Returns:
        tuple: A tuple containing:
            - str: S3 bucket name
            - str: S3 key
    """
    parsed_url = urlparse(url)
    if parsed_url.scheme != scheme:
        raise ValueError(
            "Expecting '{}' scheme, got: {} in {}.".format(
                scheme,
                parsed_url.scheme,
                url
            )
        )
    return parsed_url.netloc, parsed_url.path.lstrip("/")

def zip_folder(dir_path, output_file, rm_original=True):
    """zip in directory and optionally throw away unzipped"""

    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file in _iter_nested_dir(dir_path):
            if file.name != Path(output_file).name and file.is_file():
                zipf.write(os.path.join(file), arcname=file.relative_to(dir_path))
                if rm_original:
                    _delete_file(file)

def zip_folder_as_tarfile(dir_path, output_file, rm_original=True):
    """zip folder as tarfile and optionally throw away original files"""
    with tarfile.open(output_file, "w:gz") as tar:
        for file in _iter_nested_dir(dir_path):
            if file.name != Path(output_file).name and file.is_file():
                tar.add(file, arcname=file.relative_to(dir_path))
                if rm_original:
                    _delete_file(file)

def unzip_file(filename, output_dir, rm_zipped=True):
    """unzip in directory and optionally throw away zipped"""
    with zipfile.ZipFile(filename, 'r', zipfile.ZIP_DEFLATED) as zipf:
        logger.info(
            "Unzipping {ZIP_FILE} => {OUTPUT_DIR}".format(
                ZIP_FILE=filename,
                OUTPUT_DIR=output_dir
            )
        )
        zipf.extractall(output_dir)
        if rm_zipped:
            logger.info("Removing {}".format(filename))
            _delete_file(filename)

def unzip_file_from_tarfile(filename, output_dir, rm_zipped=True):
    """untar in directory and optionally throw away zipped"""
    with tarfile.open(filename, "r:gz") as tar:
        logger.info("Unzipping {ZIP_FILE} => {OUTPUT_DIR}".format(
                ZIP_FILE=filename,
                OUTPUT_DIR=output_dir
            )
        )
        tar.extractall(output_dir)
        if rm_zipped:
            logger.info("Removing {FILE_PATH}".format(FILE_PATH=filename))
            _delete_file(filename)

def strip_scheme(url: str):
    """strip scheme from url"""
    parsed = urlparse(url)
    scheme = "{SCHEME}://".format(SCHEME=parsed.scheme)
    return parsed.geturl().replace(scheme, '', 1)

def _read_json(file_path):
    """Read a JSON file.
    Args:
        path (str): Path to the file.
    Returns:
        (dict[object, object]): A dictionary representation of the JSON file.
    """
    with open(file_path, "r") as file_:
        return json.load(file_)

def _write_json(obj, file_path):
    """Write a serializeable object as a JSON file."""
    with open(file_path, "w") as file_:
        json.dump(obj, file_, indent=4)
        file_.write('\n')

def _write_file(file_path: str, parents: bool =True):
    """write a file"""
    if parents is True:
        mkpath(str(Path(file_path).parents[0].absolute()))
    write_file(str(Path(file_path).absolute()), '')

def _rename_file(base_path, current_filename, new_filename):
    """renames filename for a given base_path, saving the file in the same base_path

    Args:
        base_path ([type]): directory path containing file to rename
        current_filename ([type]): current name of the file to rename
        new_filename ([type]): new name for the renamed file
    """
    Path(base_path, current_filename).rename(Path(base_path, new_filename))

def _create_empty_file(base_path, filename):
    """renames filename for a given base_path, saving the file in the same base_path

    Args:
        base_path ([type]): directory path containing file to rename
        current_filename ([type]): current name of the file to rename
        new_filename ([type]): new name for the renamed file
    """
    Path(base_path, filename).touch(exist_ok=True)

def _copy_boilerplate_to_dst(src: str, dst: str, remove_first=False):
    """[summary]

    Args:
        src (str): [description]
        dst (str): [description]
    """
    source_path = str(Path(src).absolute())
    destination_path = str(Path(dst).absolute())
    if remove_first is True:
        try:
            logger.debug("removing first")
            remove_tree(destination_path)
        except FileNotFoundError:
            logger.debug("No file found. Assuming already deleted.")
    _ = copy_tree(source_path, destination_path)

@contextlib.contextmanager
def set_env(**environ):
    """
    Temporarily set the process environment variables.

    >>> with set_env(PLUGINS_DIR=u'test/plugins'):
    ...   "PLUGINS_DIR" in os.environ
    True

    >>> "PLUGINS_DIR" in os.environ
    False

    :type environ: dict[str, unicode]
    :param environ: Environment variables to set
    """
    old_environ = dict(os.environ)
    os.environ.update(environ)
    try:
        yield
    finally:
        os.environ.clear()
        os.environ.update(old_environ)

def get_env_vars(environment, regex, flat=True):
    """Get all environ vars matching contains='<PREFIX>'"""
    if flat:
        filtered_env_vars = []
    else:
        filtered_env_vars = {}

    regex_pattern = re.compile(regex)

    for key,value in environment.items():
        result = regex_pattern.match(key)
        if result:
            # get all keys matching the regex
            if flat:
                filtered_env_vars.append({'key': key, 'value': value})
            else:
                filtered_env_vars.update({key: value})
    return filtered_env_vars

def get_sdk_credentials_volume_mount(
    auth_type='gcloud',
    **kwargs
):
    """
        configures a volume mount for providing provider resource
        permissions.
    """

    if auth_type == 'gcloud':
        host_path = kwargs.get('host_path', '~/.config/gcloud')
        container_path = kwargs.get('container_path', '/root/.config/gcloud')
    elif auth_type == 'awscli':
        host_path = kwargs.get('host_path', '~/.aws')
        container_path = kwargs.get('container_path', '/root/.aws')
    else:
        raise Exception("AUTH_TYPE = {} is not currently supported.")

    host_volume = Path(os.path.expanduser(host_path)).absolute().as_posix()
    container_bind = {'bind': container_path, 'mode': 'rw'}
    return {host_volume: container_bind}

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
            logger.info("Downloading {CONTENT_PATH}".format(CONTENT_PATH=content.path))
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
    except (GithubException, IOError):

        # get exc info
        exc_type, _, _ = sys.exc_info()

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

def download_from_git(github, start_dir, org, repo, branch, root: str = '.'):
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
