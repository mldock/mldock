import os
import environs
import json
from pathlib import Path
import logging

from mldock.platform_helpers import utils


logger = logging.getLogger('mldock')

class AbstractEnvironment:

    def get_input_channel_iter(self):
        """Returns: Iterable of the input channels
        """
        return list()

    def get_output_channel_iter(self):
        """Returns: Iterable of the output channel
        """
        return list()

    def get_model_input_channel_iter(self):
        """Returns: Iterable of the model input channels
        """
        return list()
        
    def get_model_output_channel_iter(self):
        """Returns: Iterable of the model output channels
        """
        return list()

    def setup_inputs(self):
        """ Iterates and downloads assets remoate -> input channels
            return:
                None
        """
        pass

    def cleanup_outputs(self):
        """ Iterates and uploads output channel -> remote
            return:
                None
        """
        pass

    def setup_model_artifacts(self):
        """ Iterates and downloads assets remoate -> model channel
            return:
                None
        """
        pass

    def cleanup_model_artifacts(self):
        """ Iterates and uploads from model channel -> remote
            return:
                None
        """
        pass


class BaseEnvironment(AbstractEnvironment):

    input_channel_regex = None
    model_channel_regex = None
    output_channel_regex = None
    output_channel_regex = None
    hyperparameters_file = None
    environment_variables = environs.Env()

    def __init__(self, base_dir, **kwargs):

        self.environment_variables.read_env()
        self.base_dir = base_dir
        self.hyperparameters_file = kwargs.get(
            'hyperparameters_file', 'hyperparameters.json'
        )

        self.input_channel_regex = kwargs.get(
            'input_channel_regex', r'MLDOCK_INPUT_CHANNEL_.*'
        )
        self.model_input_channel_regex = kwargs.get(
            'model_input_channel_regex', r'MLDOCK_MODEL_INPUT_CHANNEL.*'
        )

        self.model_output_channel_regex = kwargs.get(
            'model_output_channel_regex', r'MLDOCK_MODEL_OUTPUT_CHANNEL.*'
        )

        self.output_channel_regex = kwargs.get(
            'output_channel_regex', r'MLDOCK_OUTPUT_CHANNEL_.*'
        )
        self.hyperparamters_env_variable = kwargs.get(
            'hyperparamters_regex', r'MLDOCK_HYPERPARAMETERS'
        )

        self._create_training_directories()
        self.setup_hyperparameters()

    def _create_training_directories(self):
        """Create the directory structure, if not exists
        """
        logger.debug("Creating a new training folder under {} .".format(self.base_dir))

        try:
            self.input_data_dir.mkdir(parents=True, exist_ok=True)
            self.model_dir.mkdir(parents=True, exist_ok=True)
            self.input_config_dir.mkdir(parents=True, exist_ok=True)
            self.output_data_dir.mkdir(parents=True, exist_ok=True)
            if not self.hyperparameters_filepath.exists():
                utils._write_json(
                    obj={},
                    file_path=self.hyperparameters_filepath
                )
        except Exception as exception:
            logger.error(exception)

    @property
    def input_dir(self):
        return Path(self.base_dir, 'input')

    @property
    def input_data_dir(self):
        return Path(self.input_dir, 'data')

    @property
    def input_config_dir(self):
        return Path(self.input_dir, 'config')

    @property
    def hyperparameters_filepath(self):
        return Path(self.input_config_dir, self.hyperparameters_file)

    @property
    def model_dir(self):
        return Path(self.base_dir, 'model')
    
    @property
    def output_data_dir(self):
        return Path(self.base_dir, 'output')

    @property
    def hyperparameters(self):
        """Returns: Iterable of the input channels
        """
        return utils._read_json(
            self.hyperparameters_filepath
        )

    def setup_hyperparameters(self):
        """Retrieves the env vars matching hyperparameters regex and updates config"""
        hyperparameters = utils._read_json(
            self.hyperparameters_filepath.as_posix()
        )

        updated_hparams = self.environment_variables.json(self.hyperparamters_env_variable, '{}')

        hyperparameters.update(
            updated_hparams
        )

        utils._write_json(
            obj=hyperparameters,
            file_path=self.hyperparameters_filepath.as_posix()
        )

    def get_input_channel_iter(self):
        """Returns: Iterable of the input channels
        """
        envvars = dict(os.environ)
        return utils.get_env_vars(environment=envvars, regex=self.input_channel_regex)

    def get_output_channel_iter(self):
        """Returns: Iterable of the output channel
        """
        envvars = dict(os.environ)
        return utils.get_env_vars(environment=envvars, regex=self.output_channel_regex)

    def get_model_input_channel_iter(self):
        """Returns: Iterable of the model channel
        """
        envvars = dict(os.environ)
        return utils.get_env_vars(environment=envvars, regex=self.model_input_channel_regex)

    def get_model_output_channel_iter(self):
        """Returns: Iterable of the model channel
        """
        envvars = dict(os.environ)
        return utils.get_env_vars(environment=envvars, regex=self.model_output_channel_regex)