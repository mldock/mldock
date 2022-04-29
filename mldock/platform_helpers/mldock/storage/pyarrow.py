"""PYARROW STORAGE HELPERS"""
import tempfile
from pathlib import Path
import logging
from pyarrow import fs

from mldock.platform_helpers import utils

logger = logging.getLogger("mldock")


def get_file_info(file_system: fs.FileSystem, artifacts_base_path: str):
    """Get file(s) info for download from pyarrow.fs.FileSystem

    Args:
        file_system (fs.FileSystem): a pyarrow supported file system object
        artifacts_base_path (str): full path including bucket name if remote filesystem

    Returns:
        List[str | pyarrow.fs.FileInfo]: file paths
    """
    if isinstance(file_system, fs.LocalFileSystem):
        file_selector = file_system.get_file_info(artifacts_base_path)

        if file_selector.is_file:
            files = [file_selector.path]
        else:
            file_selector = fs.FileSelector(artifacts_base_path, recursive=True)

            files = [file_.path for file_ in file_system.get_file_info(file_selector)]

    else:

        if file_system.isfile(artifacts_base_path):
            file_selector = file_system.info(artifacts_base_path)
            files = [file_selector["name"]]
        else:

            files = file_system.glob(Path(artifacts_base_path, "**").as_posix())

    return files


def upload_assets(
    file_system: fs.FileSystem,
    fs_base_path: str,
    storage_location: str,
    local_path: str,
):
    """
    Uploads logs to specified file-system
    Args:
        file_system (fs.FileSystem): a pyarrow supported file system object
        fs_base_path (str): base path including bucket name if remote filesystem
        storage_location (str): relative location to base path
    """

    is_directory = Path(local_path).is_dir()
    if is_directory:
        # if is a directory, zip
        # pylint: disable=consider-using-with
        tmp_dir = tempfile.TemporaryDirectory()
        new_local_path = Path(tmp_dir.name, "artifacts.zip")
        utils.zip_folder(local_path, new_local_path, rm_original=False)
        local_path = new_local_path

    # create full artifacts base path
    artifacts_base_path = Path(fs_base_path, storage_location)

    src_path = Path(local_path)
    file_name = src_path.name
    dst_path = Path(artifacts_base_path, file_name)

    if isinstance(file_system, fs.LocalFileSystem):
        artifacts_base_path.mkdir(parents=True, exist_ok=True)
        file_system.copy_file(src_path.as_posix(), dst_path.as_posix())
    else:
        file_system.upload(src_path.as_posix(), dst_path.as_posix())

    if is_directory:
        tmp_dir.cleanup()


def download_assets(
    file_system: fs.FileSystem,
    fs_base_path: str,
    storage_location: str,
    local_path: str,
):
    """
    Uploads logs to specified file-system
    Args:
        file_system (fs.FileSystem): a pyarrow supported file system object
        fs_base_path (str): base path including bucket name if remote filesystem
        storage_location (str): relative location to base path
    """
    artifacts_base_path = Path(fs_base_path, storage_location)
    files = get_file_info(
        file_system=file_system, artifacts_base_path=artifacts_base_path.as_posix()
    )

    for file in files:

        src_path = Path(file)
        file_name = src_path.name
        dst_path = Path(local_path, file_name)
        dst_path.parents[0].mkdir(parents=True, exist_ok=True)

        logger.info(f"downloading {src_path.as_posix()}")

        if isinstance(file_system, fs.LocalFileSystem):
            artifacts_base_path.mkdir(parents=True, exist_ok=True)
            file_system.copy_file(src_path.as_posix(), dst_path.as_posix())
        else:

            file_system.download(src_path.as_posix(), dst_path.as_posix())

        if dst_path.suffix == ".zip":

            utils.unzip_file(dst_path, local_path, rm_zipped=True)

        elif dst_path.suffix == ".gz":

            utils.unzip_file_from_tarfile(dst_path, local_path, rm_zipped=True)
        else:
            logger.info(
                f"skipping: {dst_path} is not a compressed file or compression format is not supported."
            )
