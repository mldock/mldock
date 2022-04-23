import tempfile
from pathlib import Path
from mldock.platform_helpers import utils
from mldock.platform_helpers.mldock.asset_managers.base import BaseEnvArtifactManager
from mock import patch
from pyarrow import fs
from mldock.platform_helpers.mldock.storage.pyarrow import (
    download_assets,
    upload_assets,
)

class ExampleLocalEnvArtifactManager(BaseEnvArtifactManager):
    """Example of an artifact manager to inherits from the abstract class"""

    @staticmethod
    def download_assets(fs_base_path, local_path, storage_location):
        file_system = fs.LocalFileSystem()
        download_assets(
            file_system,
            fs_base_path=fs_base_path,
            local_path=local_path,
            storage_location=storage_location
        )

    def upload_assets(self, **kwargs):
        file_system = fs.LocalFileSystem()
        upload_assets(
                    file_system,
                    **kwargs
                )

class TestBaseEnvArtifactManager:
    """test base environment artifact manager"""

    # helpers
    @staticmethod
    def __create_textfile(my_path):
        """creates textfile and seeds it with msg"""
        # This currently assumes the path to the file exists.
        msg = "test that this works"

        parent_path = Path(my_path).parent
        parent_path.mkdir(parents=True, exist_ok=True)
        with open(my_path, "w+") as file:
            file.write(msg)
        return msg

    def test_setup_inputs_success(self):
        """test setup all inputs (data and models) works correctly with environment variables"""
        with tempfile.TemporaryDirectory() as result_tempdir:
                input_tempdir = tempfile.TemporaryDirectory("input_example")
                txtfile = Path(input_tempdir.name, "data.txt")
                _ = self.__create_textfile(txtfile)

                input_model_tempdir = tempfile.TemporaryDirectory("input_model_example")
                txtfile = Path(input_model_tempdir.name, "model.pkl")
                _ = self.__create_textfile(txtfile)
                env_vars = {
                    "MLDOCK_INPUT_CHANNEL_EXAMPLE": input_tempdir.name,
                    "MLDOCK_MODEL_INPUT_CHANNEL_EXAMPLE": input_model_tempdir.name,
                    "MLDOCK_BASE_DIR": result_tempdir
                }

                with utils.set_env(**env_vars):

                    artifact_manager = ExampleLocalEnvArtifactManager()
                    artifact_manager.setup_inputs()
                    artifact_manager.setup_model_artifacts()

                assert Path(result_tempdir, 'input/data/example/data.txt').exists(), "Failure."
                assert Path(result_tempdir, 'model/example/model.pkl').exists(), "Failure."

                input_tempdir.cleanup()
                input_model_tempdir.cleanup()

    def test_cleanup_outputs_success(self):
        """test setup all inputs (data and models) works correctly with environment variables"""
        with tempfile.TemporaryDirectory() as result_tempdir:

                txtfile = Path(result_tempdir, "output/example/data.txt")
                _ = self.__create_textfile(txtfile)

                txtfile = Path(result_tempdir, "model/example/model.txt")
                _ = self.__create_textfile(txtfile)
    
                print(list(Path(result_tempdir).glob("*/*/*")))

                output_tempdir = tempfile.TemporaryDirectory("output_example")
                result_output_data_path = Path(output_tempdir.name, "data/example")
                result_output_model_path = Path(output_tempdir.name, "model/example")

                env_vars = {
                    "MLDOCK_OUTPUT_CHANNEL_EXAMPLE": Path(result_output_data_path, "data.txt").as_posix(),
                    "MLDOCK_MODEL_OUTPUT_CHANNEL_EXAMPLE": result_output_model_path.as_posix(),
                    "MLDOCK_BASE_DIR": result_tempdir
                }

                with utils.set_env(**env_vars):

                    artifact_manager = ExampleLocalEnvArtifactManager()
                    artifact_manager.cleanup_outputs()
                    artifact_manager.cleanup_model_artifacts()

                print(list(Path(output_tempdir.name).glob("*/*/*")))

                assert Path(output_tempdir.name, "data/example/data.txt").exists(), "Failure."
                assert Path(output_tempdir.name, 'model/example/artifacts.zip').exists(), "Failure."

                output_tempdir.cleanup()
