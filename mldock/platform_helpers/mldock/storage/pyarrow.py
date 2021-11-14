"""PYARROW STORAGE HELPERS"""
import tempfile
from pathlib import Path
import logging
from pyarrow import fs

from mldock.platform_helpers import utils

logger = logging.getLogger("mldock")


def upload_assets(
    file_system, fs_base_path, local_path, storage_location, zip_artifacts: bool = False
):
    """Uploads logs to specified file-system"""

    if zip_artifacts:
        # pylint: disable=consider-using-with
        tmp_dir = tempfile.TemporaryDirectory()
        utils.zip_folder(
            local_path, Path(tmp_dir.name, "artifacts.zip"), rm_original=False
        )
        local_path = tmp_dir.name

    # create full artifacts base path
    artifacts_base_path = Path(fs_base_path, storage_location)

    local = fs.LocalFileSystem()

    file_selector = fs.FileSelector(local_path, recursive=True)
    for file in local.get_file_info(file_selector):
        src_path = Path(file.path)
        file_name = src_path.name
        dst_path = Path(artifacts_base_path, file_name)

        if isinstance(file_system, fs.LocalFileSystem):
            artifacts_base_path.mkdir(parents=True, exist_ok=True)
            file_system.copy_file(src_path.as_posix(), dst_path.as_posix())
        else:
            file_system.upload(src_path.as_posix(), dst_path.as_posix())

    if zip_artifacts:
        tmp_dir.cleanup()


def download_assets(file_system, fs_base_path, local_path, storage_location):
    """Uploads logs to specified file-system"""

    # create full artifacts base path
    artifacts_base_path = Path(fs_base_path, storage_location)

    if isinstance(file_system, fs.LocalFileSystem):
        file_selector = fs.FileSelector(fs_base_path, recursive=True)

        file_selector = file_system.get_file_info(file_selector)
    else:
        file_selector = file_system.glob(Path(artifacts_base_path, "**").as_posix())

    for file in file_selector:
        if isinstance(file, fs.FileInfo):
            file = file.path
        src_path = Path(file)
        file_name = src_path.name
        dst_path = Path(local_path, file_name)
        dst_path.parents[0].mkdir(parents=True, exist_ok=True)

        if isinstance(file_system, fs.LocalFileSystem):
            artifacts_base_path.mkdir(parents=True, exist_ok=True)
            file_system.copy_file(src_path.as_posix(), dst_path.as_posix())
        else:
            logger.info(src_path.as_posix())
            file_system.download(src_path.as_posix(), dst_path.as_posix())

            if Path(file).suffix == ".zip":

                utils.unzip_file(dst_path, local_path, rm_zipped=True)

            elif Path(file).suffix == ".gz":

                utils.unzip_file_from_tarfile(dst_path, local_path, rm_zipped=True)
