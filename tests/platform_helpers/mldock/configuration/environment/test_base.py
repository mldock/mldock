"""TEST ENVIRONMENT UTILITIES"""
import os
import json
import tempfile
from pathlib import Path

from mldock.platform_helpers import utils
from mldock.platform_helpers.mldock.configuration.environment.base import \
    BaseEnvironment

class TestBaseEnvironment:
    """Collection of tests to test base environment"""
    @staticmethod
    def test_create_training_directories_success():
        """Test Environment class instantiates directories successfully"""
        with tempfile.TemporaryDirectory() as tempdir:
            # you can e.g. create a file here:
            container_opt = Path(tempdir)
            environment = BaseEnvironment(base_dir=container_opt)

            root_dir_tree = [p.relative_to(tempdir).as_posix() for p in container_opt.glob('*')]

            input_dir_tree = [p.relative_to(tempdir).as_posix() for p in Path(container_opt,'input').glob('*')]

            assert root_dir_tree == ['input', 'output', 'model'], "Fail. Root directories were not created successfully"

            assert input_dir_tree == ['input/data', 'input/config'], "Fail. Root directories were not created successfully"

    @staticmethod
    def test_environment_properties_with_expected_paths():
        """Test Environment class provides the correct/expected paths for properties"""
        with tempfile.TemporaryDirectory() as tempdir:
            # you can e.g. create a file here:
            container_opt = Path(tempdir)
            environment = BaseEnvironment(base_dir=container_opt)


            assert environment.input_dir == Path(container_opt, 'input'), "Fail. Input directory did not match"

            assert environment.input_data_dir == Path(container_opt, 'input/data'), "Fail. Input Data directory did not match"
            assert environment.input_config_dir == Path(container_opt, 'input/config'), "Fail. Input Config directory did not match"
            
            assert environment.model_dir == Path(container_opt, 'model'), "Fail. Model directory did not match"
            assert environment.output_data_dir == Path(container_opt, 'output'), "Fail. Output directory did not match"

    @staticmethod
    def test_setup_hyperparameters_is_correct():
        """Test Environment class provides the correct/expected paths for properties"""
        with tempfile.TemporaryDirectory() as tempdir:
            # you can e.g. create a file here:
            container_opt = Path(tempdir)

            hyperparameters = {"key": "value", "factors": 1, "decision": False}

            env_vars = {
                "MLDOCK_HYPERPARAMETERS": json.dumps(hyperparameters)
            }

            valid_vars = [{"key": key, 'value': value} for key,value in env_vars.items()]

            with utils.set_env(**env_vars):
                environment = BaseEnvironment(base_dir=container_opt)
                assert environment.hyperparameters == hyperparameters, "Fail. Hyperparameters did not match expected"

    @staticmethod
    def test_get_input_channel_iter():
        """Test Environment class provides the correct/expected input channels"""
        with tempfile.TemporaryDirectory() as tempdir:
            # you can e.g. create a file here:
            container_opt = Path(tempdir)

            env_vars = {
                "MLDOCK_INPUT_CHANNEL_EXAMPLE": "s3://bucket/data/example/"
            }

            valid_vars = [{"key": key, 'value': value} for key,value in env_vars.items()]

            with utils.set_env(**env_vars):
                environment = BaseEnvironment(base_dir=container_opt)
                assert environment.get_input_channel_iter()[0] == {
                    'key': 'MLDOCK_INPUT_CHANNEL_EXAMPLE',
                    'value': 's3://bucket/data/example/'
                }, "Fail. Input Channel 'example' was not found"

    @staticmethod
    def test_get_output_channel_iter():
        """Test Environment class provides the correct/expected output channels"""
        with tempfile.TemporaryDirectory() as tempdir:
            # you can e.g. create a file here:
            container_opt = Path(tempdir)

            env_vars = {
                "MLDOCK_OUTPUT_CHANNEL_EXAMPLE": "s3://bucket/data/output/example"
            }

            valid_vars = [{"key": key, 'value': value} for key,value in env_vars.items()]

            with utils.set_env(**env_vars):
                environment = BaseEnvironment(base_dir=container_opt)
                assert environment.get_output_channel_iter()[0] == {
                    'key': 'MLDOCK_OUTPUT_CHANNEL_EXAMPLE',
                    'value': "s3://bucket/data/output/example"
                }, "Fail. Output Channel 'example' was not found"

    @staticmethod
    def test_get_model_output_channel_iter():
        """Test Environment class provides the correct/expected model input channels"""
        with tempfile.TemporaryDirectory() as tempdir:
            # you can e.g. create a file here:
            container_opt = Path(tempdir)

            env_vars = {
                "MLDOCK_MODEL_INPUT_CHANNEL_EXAMPLE": "s3://bucket/model/example"
            }

            valid_vars = [{"key": key, 'value': value} for key,value in env_vars.items()]

            with utils.set_env(**env_vars):
                environment = BaseEnvironment(base_dir=container_opt)
                assert environment.get_model_input_channel_iter()[0] == {
                    'key': 'MLDOCK_MODEL_INPUT_CHANNEL_EXAMPLE',
                    'value': "s3://bucket/model/example"
                }, "Fail. Output Channel 'example' was not found"

    @staticmethod
    def test_get_model_output_channel_iter():
        """Test Environment class provides the correct/expected model output channels"""
        with tempfile.TemporaryDirectory() as tempdir:
            # you can e.g. create a file here:
            container_opt = Path(tempdir)

            env_vars = {
                "MLDOCK_MODEL_OUTPUT_CHANNEL_EXAMPLE": "s3://bucket/model/example"
            }

            valid_vars = [{"key": key, 'value': value} for key,value in env_vars.items()]

            with utils.set_env(**env_vars):
                environment = BaseEnvironment(base_dir=container_opt)
                assert environment.get_model_output_channel_iter()[0] == {
                    'key': 'MLDOCK_MODEL_OUTPUT_CHANNEL_EXAMPLE',
                    'value': "s3://bucket/model/example"
                }, "Fail. Output Channel 'example' was not found"
