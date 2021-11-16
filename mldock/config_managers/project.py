"""
    Container Project Config manager

    Config Managers that create and update the container project config.
    Currently supported:
        - mldock
"""
import os
import sys
import logging
from pathlib import Path
import click

from mldock.terminal import ChoiceWithNumbers, style_dropdown
from mldock.config_managers.core import BaseConfigManager
from mldock.platform_helpers.mldock import utils as mldock_utils
from mldock.platform_helpers import utils

logger = logging.getLogger("mldock")


class MLDockConfigManager(BaseConfigManager):
    """Hyperparameter Config Manager for mldock"""

    config = {
        "image_name": None,
        "template": "generic",
        "requirements_dir": "src/requirements.txt",
        "mldock_module_dir": "src",
        "container_dir": "container",
        "data": [],
        "environment": {},
        "hyperparameters": {},
        "model": [],
        "stages": {},
    }

    available_templates = None

    def __init__(self, filepath: str, create: bool = False, **kwargs):
        # dealing with weird os related path formats
        super().__init__()
        self.filepath = filepath
        self.available_templates = kwargs.get("available_templates", None)

        config = self.load_config(self.filepath, create=create)

        self.image_name_default = Path(filepath).parents[0].name

        self.config.update(config)

        if self.config.get("image_name", None) is None:
            # if is None override with default
            self.config["image_name"] = self.image_name_default

    def check_if_exists_else_create(self, file_name: str, create: bool):
        """check that mldock fileexists"""
        if not self.file_exists(file_name):
            if create:
                # deal with possiblity of nested directory
                utils._mkdir(Path(file_name).parents[0])
                # create file
                self.touch(file_name)
            else:
                logger.error(
                    (
                        "No MLDOCK container project found with "
                        "dir = '{CONTAINER_DIR}/'. Re-run `mldock project init` "
                        "and Confirm 'yes' to create.".format(
                            CONTAINER_DIR=Path(file_name).parents[0]
                        )
                    )
                )
                sys.exit(1)

    def setup_config(self):
        """run setup for configuration"""
        click.secho("Base Setup", bg="blue")
        self.ask_for_image_name()
        self.ask_for_template_name()
        self.ask_for_mldock_module_dir()
        self.ask_for_container_dir_name()
        self.ask_for_requirements_file_name()

    def update_config(self, **kwargs):
        """update configuration with given kwargs"""
        self.config.update(kwargs)

    def ask_for_image_name(self):
        """prompt user for image name"""
        image_name = click.prompt(
            text=click.style("Set your image name: ", fg="bright_blue"),
            default=self.config.get("image_name", self.image_name_default),
        )

        self.config.update({"image_name": image_name})

    def ask_for_template_name(self):
        """prompt user for container project template name"""

        click.secho("Set container project template name", bg="blue", nl=True)
        # would be awesome to fetch this from the template dir
        options = self.available_templates

        template_name = click.prompt(
            text=style_dropdown(
                group_name="template name",
                options=options,
                default=self.config.get("template", "generic"),
            ),
            type=ChoiceWithNumbers(options, case_sensitive=False),
            show_default=True,
            default=self.config.get("template", "generic"),
            show_choices=False,
        )

        self.config.update({"template": template_name})

    def ask_for_container_dir_name(self):
        """prompt user for container dir name"""
        container_dir_name = click.prompt(
            text=click.style("Set your container dir name: ", fg="bright_blue"),
            default=self.config.get("container_dir", "container"),
        )

        self.config.update({"container_dir": container_dir_name})

    def ask_for_mldock_module_dir(self):
        """prompt user for mldock module dir"""

        mldock_module_dir = click.prompt(
            text=click.style("Set mldock module dir: ", fg="bright_blue"),
            default=self.config.get("mldock_module_dir", "src"),
        )

        self.config.update({"mldock_module_dir": mldock_module_dir})

    @staticmethod
    def _format_data_node_item(item, base_path="data"):

        new_key = item["channel"]
        new_value = os.path.join(base_path, item["channel"], item["filename"])
        return "\t{KEY} : {VALUE}".format(KEY=new_key, VALUE=new_value)

    def _format_data_node(self):

        output = []

        for item in self.config["data"]:
            output.append(self._format_data_node_item(item, base_path="data"))

        return "\n".join(output)

    def _format_model_node(self):

        output = []

        for item in self.config["model"]:
            output.append(self._format_data_node_item(item, base_path="model"))

        return "\n".join(output)

    def _format_stage_node(self):

        output = []

        for key_, value_ in self.config["stages"].items():
            image_and_tag = "{}:{}".format(self.config["image_name"], value_["tag"])
            output.append("\t{} : {}".format(key_, image_and_tag))

        return "\n".join(output)

    @staticmethod
    def _format_nodes(config):

        output = []

        for key_, value_ in config.items():
            output.append("\t{} : {}".format(key_, value_))

        return "\n".join(output)

    def get_state(self):
        """pretty prints a json config to terminal"""
        config = self.config.copy()

        config.pop("stages")
        formatted_stages = self._format_stage_node()
        hyperparameters = config.pop("hyperparameters")
        config.pop("data")
        formatted_data_node = self._format_data_node()
        config.pop("model")
        formatted_model_node = self._format_model_node()
        environment = {}
        for key_, value_ in config.pop("environment").items():
            mldock_key = mldock_utils._format_key_as_mldock_env_var(
                key_, prefix="mldock"
            )
            environment.update({mldock_key: value_})

        states = []

        states.append({"name": "Base Setup", "message": self._format_nodes(config)})
        states.append({"name": "Data Channels", "message": formatted_data_node})
        states.append({"name": "Model Channels", "message": formatted_model_node})
        states.append({"name": "Stages", "message": formatted_stages})
        states.append(
            {"name": "Hyperparameters", "message": self._format_nodes(hyperparameters)}
        )
        states.append(
            {
                "name": "Environment Variables",
                "message": self._format_nodes(environment),
            }
        )

        return states

    def ask_for_requirements_file_name(self):
        """prompt user for image name"""
        requirements_file_name = click.prompt(
            text=click.style("Set full path to requirements: ", fg="bright_blue"),
            default=self.config.get("requirements_dir", "requirements.txt"),
        )

        self.config.update({"requirements_dir": requirements_file_name})

    def update_stages(self, stages: dict):
        """update stages node in .mldock config"""
        self.config.update({"stages": stages})

    def update_env_vars(self, environment: dict):
        """
        Update environment node in .mldock config

        Args:
            environment (dict): key,value dictionaries
        """
        self.config.update({"environment": environment})

    def update_hyperparameters(self, hyperparameters: dict):
        """
        Update hyperparameter node in .mldock config

        Args:
            hyperparameters (dict): key,value dictionaries
        """
        self.config.update({"hyperparameters": hyperparameters})

    def update_data_channels(self, data: dict):
        """
        Update data node in .mldock config

        Args:
            data (dict): key,value dictionaries
        """
        self.config.update({"data": data})

    def update_model_channels(self, models: dict):
        """
        Update data node in .mldock config

        Args:
            data (dict): key,value dictionaries
        """
        self.config.update({"model": models})
