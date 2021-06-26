"""
    Core config managers

    Config managers that are reused across mldock cli tool.
"""
import os
import json
import click
import logging
from pathlib import Path

from mldock.platform_helpers import utils


logger=logging.getLogger('mldock')

class WorkingDirectoryManager:
    """Base config manager with basic read, write and update functionality.
    """
    def __init__(self, base_dir):
        self.base_dir = base_dir
        prompt_input = True

        if not self.file_exists(self.base_dir):
            prompt_input = click.prompt("File not found. Create?", default="yes")

            if prompt_input:
                self.base_dir.mkdir(parents=True, exist_ok=True)

        self.make_asset_dirs()

    def get_working_dir(self):
        return self.base_dir

    def make_asset_dirs(self):
        """Create the directory structure, if not exists
        """
        logger.debug("Creating assets directories in working dir {} .".format(self.base_dir))

        try:
            self.input_data_dir.mkdir(parents=False, exist_ok=True)
            self.input_config_dir.mkdir(parents=False, exist_ok=True)
            self.model_dir.mkdir(parents=False, exist_ok=True)
            self.output_data_dir.mkdir(parents=False, exist_ok=True)

        except Exception as exception:
            logger.error(exception)

    @staticmethod
    def file_exists(filename: str) -> bool:
        """Check if file exists

        Args:
            filename (str): path to file

        Returns:
            bool: whether file exists
        """
        return os.path.exists(filename)

    @property
    def input_data_dir(self):
        return Path(self.base_dir, 'data')

    @property
    def input_config_dir(self):
        return Path(self.base_dir, 'config')

    @property
    def model_dir(self):
        return Path(self.base_dir, 'model')
    
    @property
    def output_data_dir(self):
        return Path(self.base_dir, 'output')

class BaseConfigManager:
    """Base config manager with basic read, write and update functionality.
    """
    def __init__(self, filepath: str, create: bool = False):
        self.filepath = filepath

        self.config = self.load_config(self.filepath, create=create)

    @staticmethod
    def touch(path: str):
        """create a blank json file, seeded with {}

        Args:
            path (str): path to file
        """
        logger.info(path)
        with open(path, 'a') as file_:
            json.dump({}, file_)

    @staticmethod
    def file_exists(filename: str) -> bool:
        """Check if file exists

        Args:
            filename (str): path to file

        Returns:
            bool: whether file exists
        """
        return os.path.exists(filename)

    def check_if_exists_else_create(self,file_name: str, create: bool):
        if not self.file_exists(file_name):
            if create:
                # deal with possiblity of nested directory
                utils._mkdir(Path(file_name).parents[0])
                # create file
                self.touch(file_name)

    def load_config(self, file_name: str, create: bool) -> dict:
        """loads config from file

        Args:
            filename (str): path to config to load
        Returns:
            dict: config
        """        
        self.check_if_exists_else_create(
            file_name=file_name, create=create
        )

        with open(file_name, "r") as file_:
            config = json.load(file_)
            return config

    def pretty_print(self):
        """pretty prints a json config to terminal
        """
        pretty_config = json.dumps(self.config, indent=4, separators=(',', ': '), sort_keys=True)
        logger.debug("{}\n".format(pretty_config))

    def write_file(self):
        """
        Trains ML model(s) locally
        :param dir: [str], source root directory
        :param docker_tag: [str], the Docker tag for the image
        :param image_name: [str], The name of the Docker image
        """
        logger.info(self.filepath)
        with open(self.filepath, 'w') as config_file:
            json.dump(self.config, config_file, indent=4, sort_keys=True)

    def get_config(self) -> dict:
        """get config object

        Returns:
            dict: config
        """
        return self.config
