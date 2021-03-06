from pathlib import Path
import tempfile
from pyarrow import fs
from mldock.platform_helpers.mldock.storage.pyarrow import (
    upload_assets,
    download_assets,
)


class TestPyarrow:

    # helpers
    @staticmethod
    def __create_textfile(my_path):
        """creates textfile and seeds it with msg"""
        # This currently assumes the path to the file exists.
        msg = "test that this works"
        Path(my_path).parent.mkdir(parents=True, exist_ok=True)
        with open(my_path, "w+") as file:
            file.write(msg)
        return msg

    # tests

    def test_local_upload_assets_successfully_upload_assets_when_directory(self):
        """test local upload assets workflow"""
        local_file_system = fs.LocalFileSystem()

        with tempfile.TemporaryDirectory(suffix="data") as tmp_dir1:
            with tempfile.TemporaryDirectory() as tmp_dir2:
                txtfile = Path(tmp_dir1, "data.txt").as_posix()
                _ = self.__create_textfile(txtfile)
                upload_assets(
                    file_system=local_file_system,
                    fs_base_path=tmp_dir2,
                    local_path=tmp_dir1,
                    storage_location="example",
                )

                files = [f.name for f in Path(tmp_dir2).glob("**/*") if f.is_file()]
                directories = [
                    f.name for f in Path(tmp_dir2).glob("**/*") if f.is_dir()
                ]

                assert "artifacts.zip" in files, "Failure"
                assert "example" in directories, "Failure"

    def test_local_upload_assets_successfully_upload_assets_when_file(self):
        """test local upload assets workflow"""
        local_file_system = fs.LocalFileSystem()

        with tempfile.TemporaryDirectory() as tmp_dir1:
            with tempfile.TemporaryDirectory() as tmp_dir2:
                txtfile = Path(tmp_dir1, "data.txt").as_posix()
                _ = self.__create_textfile(txtfile)

                result_path = Path(tmp_dir2, "data.txt").as_posix()
                upload_assets(
                    file_system=local_file_system,
                    fs_base_path=result_path,
                    local_path=txtfile,
                    storage_location=".",
                )

                files = [f.name for f in Path(tmp_dir2).glob("*/*") if f.is_file()]
                assert "data.txt" in files, "Failure"

    def test_local_download_assets_successfully_download_assets(self):
        """test local download assets workflow"""
        local_file_system = fs.LocalFileSystem()

        with tempfile.TemporaryDirectory() as tmp_dir1:
            with tempfile.TemporaryDirectory() as tmp_dir2:
                txtfile = Path(tmp_dir2, "example/data.txt").as_posix()
                _ = self.__create_textfile(txtfile)

                download_assets(
                    file_system=local_file_system,
                    fs_base_path=tmp_dir2,
                    local_path=tmp_dir1,
                    storage_location="example",
                )

                files = [f.name for f in Path(tmp_dir2).glob("**/*") if f.is_file()]
                directories = [
                    f.name for f in Path(tmp_dir2).glob("**/*") if f.is_dir()
                ]

        assert "data.txt" in files, "Failure"
        assert "example" in directories, "Failure"

    def test_local_download_assets_successfully_log_msg_for_non_compressed_file(
        self, capsys
    ):
        """test local download assets workflow log message for non compressed file"""
        local_file_system = fs.LocalFileSystem()

        with tempfile.TemporaryDirectory() as tmp_dir1:
            with tempfile.TemporaryDirectory() as tmp_dir2:
                txtfile = Path(tmp_dir2, "example/data.txt").as_posix()
                _ = self.__create_textfile(txtfile)

                download_assets(
                    file_system=local_file_system,
                    fs_base_path=tmp_dir2,
                    local_path=tmp_dir1,
                    storage_location="example",
                )

        result_txtfile = Path(tmp_dir1, "data.txt").as_posix()
        expected_msg = f"skipping: {result_txtfile} is not a compressed file or compression format is not supported."
        captured = capsys.readouterr().out
        assert expected_msg in captured, "Failure."
