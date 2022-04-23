"""BASE ENVIRONMENT INTERFACE"""
import os
from pathlib import Path
import logging
import environs

from mldock.platform_helpers import utils


logger = logging.getLogger("mldock")


class BaseEnvironment:
    """Base Environment to be extended for different environments"""

    # pylint: disable=too-many-instance-attributes
    input_channel_regex = None
    model_channel_regex = None
    output_channel_regex = None
    output_channel_regex = None
    hyperparameters_file = None
    environment_variables = environs.Env()

    def __init__(self, base_dir: str = None, **kwargs):

        self.environment_variables.read_env()
        self.base_dir = base_dir
        if self.base_dir is None:
            # look for it in environment
            # default to /opt/ml
            self.base_dir = self.environment_variables.str("MLDOCK_BASE_DIR", "/opt/ml")

        self.relative_input_dir = self.environment_variables.str(
            "MLDOCK_INPUT_DIR", "input"
        )
        if self.relative_input_dir is None:
            self.relative_input_dir = "input"

        self.hyperparameters_file = kwargs.get(
            "hyperparameters_file", "hyperparameters.json"
        )

        self.input_channel_regex = kwargs.get(
            "input_channel_regex", r"MLDOCK_INPUT_CHANNEL_.*"
        )
        self.model_input_channel_regex = kwargs.get(
            "model_input_channel_regex", r"MLDOCK_MODEL_INPUT_CHANNEL.*"
        )

        self.model_output_channel_regex = kwargs.get(
            "model_output_channel_regex", r"MLDOCK_MODEL_OUTPUT_CHANNEL.*"
        )

        self.output_channel_regex = kwargs.get(
            "output_channel_regex", r"MLDOCK_OUTPUT_CHANNEL_.*"
        )
        self.hyperparamters_env_variable = kwargs.get(
            "hyperparamters_regex", r"MLDOCK_HYPERPARAMETERS"
        )

        self._create_training_directories()
        self.setup_hyperparameters()

    def _create_training_directories(self):
        """Create the directory structure, if not exists"""
        logger.debug(
            (
                "Creating a new training folder under {BASE_DIR} .".format(
                    BASE_DIR=self.base_dir
                )
            )
        )

        self.input_data_dir.mkdir(parents=True, exist_ok=True)
        self.model_dir.mkdir(parents=True, exist_ok=True)
        self.input_config_dir.mkdir(parents=True, exist_ok=True)
        self.output_data_dir.mkdir(parents=True, exist_ok=True)
        if not self.hyperparameters_filepath.exists():
            utils.write_json(obj={}, file_path=self.hyperparameters_filepath)

    @property
    def input_dir(self):
        """path to input directory in working directory"""
        return Path(self.base_dir, self.relative_input_dir)

    @property
    def input_data_dir(self):
        """path to input data directory in working directory"""
        return Path(self.input_dir, "data")

    @property
    def input_config_dir(self):
        """path to input config directory in working directory"""
        return Path(self.input_dir, "config")

    @property
    def hyperparameters_filepath(self):
        """path to hyperparameter config in input config directory in working directory"""
        return Path(self.input_config_dir, self.hyperparameters_file)

    @property
    def model_dir(self):
        """path to model directory in working directory"""
        return Path(self.base_dir, "model")

    @property
    def output_data_dir(self):
        """path to output directory in working directory"""
        return Path(self.base_dir, "output")

    @property
    def hyperparameters(self):
        """Returns: Iterable of the input channels"""
        return utils.read_json(self.hyperparameters_filepath)

    def setup_hyperparameters(self):
        """Retrieves the env vars matching hyperparameters regex and updates config"""
        hyperparameters = utils.read_json(self.hyperparameters_filepath.as_posix())

        updated_hparams = self.environment_variables.json(
            self.hyperparamters_env_variable, "{}"
        )

        hyperparameters.update(updated_hparams)

        utils.write_json(
            obj=hyperparameters, file_path=self.hyperparameters_filepath.as_posix()
        )

    def get_input_channel_iter(self):
        """Returns: Iterable of the input channels"""
        envvars = dict(os.environ)
        return utils.get_env_vars(environment=envvars, regex=self.input_channel_regex)

    def get_output_channel_iter(self):
        """Returns: Iterable of the output channel"""
        envvars = dict(os.environ)
        return utils.get_env_vars(environment=envvars, regex=self.output_channel_regex)

    def get_model_input_channel_iter(self):
        """Returns: Iterable of the model channel"""
        envvars = dict(os.environ)
        return utils.get_env_vars(
            environment=envvars, regex=self.model_input_channel_regex
        )

    def get_model_output_channel_iter(self):
        """Returns: Iterable of the model channel"""
        envvars = dict(os.environ)
        return utils.get_env_vars(
            environment=envvars, regex=self.model_output_channel_regex
        )

    @staticmethod
    def setup_inputs():
        """Iterates and downloads assets remoate -> input channels
        return:
            None
        """
        # pylint: disable=unnecessary-pass
        pass

    @staticmethod
    def cleanup_outputs():
        """Iterates and uploads output channel -> remote
        return:
            None
        """
        # pylint: disable=unnecessary-pass
        pass

    @staticmethod
    def setup_model_artifacts():
        """Iterates and downloads assets remoate -> model channel
        return:
            None
        """
        # pylint: disable=unnecessary-pass
        pass

    @staticmethod
    def cleanup_model_artifacts():
        """Iterates and uploads from model channel -> remote
        return:
            None
        """
        # pylint: disable=unnecessary-pass
        pass
