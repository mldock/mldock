"""
    Project Container Config manager

    Config Managers that create and update the container project config.
    Currently supported:
        - mldock
"""
import os
import json
import click
import logging
from pathlib import Path

from mldock.terminal import ChoiceWithNumbers, style_dropdown
from mldock.config_managers.core import BaseConfigManager

logger=logging.getLogger('mldock')

class MLDockConfigManager(BaseConfigManager):
    """Hyperparameter Config Manager for mldock
    """

    config = {}

    def setup_config(self):
        click.secho("Base Setup", bg='blue')
        self.ask_for_image_name()
        self.ask_for_platform_name()
        self.ask_for_mldock_module_dir()
        self.ask_for_container_dir_name()
        self.ask_for_requirements_file_name()

    def ask_for_image_name(self):
        """prompt user for image name
        """
        image_name = click.prompt(
            text=click.style("Set your image name: ", fg='bright_blue'),
            default=self.config.get('image_name', 'my_ml_container')
        )

        self.config.update({
            'image_name':image_name
        })

    def ask_for_platform_name(self):
        """prompt user for platform name
        """

        click.secho("Set container platform type", bg='blue', nl=True)
        options = ['generic', 'sagemaker', 'gcp', 'aws']

        platform_name = click.prompt(
            text=style_dropdown(
                group_name="platform name",
                options=options,
                default=self.config.get('platform', 'generic')
            ),
            type=ChoiceWithNumbers(options, case_sensitive=False),
            show_default=True,
            default=self.config.get('platform', 'generic'),
            show_choices=False
        )
        
        self.config.update({
            'platform': platform_name
        })

    def ask_for_container_dir_name(self):
        """prompt user for container dir name
        """
        container_dir_name = click.prompt(
            text=click.style("Set your container dir name: ", fg='bright_blue'),
            default=self.config.get('container_dir', 'container')
        )

        self.config.update({
            'container_dir': container_dir_name
        })

    def ask_for_mldock_module_dir(self):
        """prompt user for mldock module dir
        """
        
        mldock_module_dir = click.prompt(
            text=click.style("Set mldock module dir: ", fg='bright_blue'),
            default=self.config.get('mldock_module_dir', 'src')
        )

        self.config.update({
            'mldock_module_dir': mldock_module_dir
        })
    
    @staticmethod
    def _format_data_node_item(item, base_path='data'):

        new_key = item["channel"]
        new_value = os.path.join(base_path, item["channel"], item["filename"])
        return "\t{KEY} : {VALUE}".format(KEY=new_key, VALUE=new_value)

    def _format_data_node(self):

        output = []
        
        for item in self.config['data']:
            output.append(self._format_data_node_item(item, base_path='data'))

        return "\n".join(output)

    def _format_model_node(self):

        output = []
        
        for item in self.config['model']:
            output.append(self._format_data_node_item(item, base_path='model'))

        return "\n".join(output)

    def _format_stage_node(self):

        output = []
        
        for key_, value_ in self.config['stages'].items():
            image_and_tag = "{}:{}".format(self.config['image_name'], value_["tag"])
            output.append("\t{} : {}".format(key_, image_and_tag))

        return "\n".join(output)

    @staticmethod
    def _format_nodes(config):

        output = []
        
        for key_, value_ in config.items():
            output.append("\t{} : {}".format(key_, value_))

        return "\n".join(output)

    def get_state(self):
        """pretty prints a json config to terminal
        """
        config = self.config.copy()

        config.pop("stages")
        formatted_stages = self._format_stage_node()
        hyperparameters = config.pop("hyperparameters")
        config.pop("data")
        formatted_data_node = self._format_data_node()
        config.pop("model")
        formatted_model_node = self._format_model_node()
        environment = config.pop("environment")

        states = []

        states.append({"name": "Base Setup", "message": self._format_nodes(config)})
        states.append({"name": "Data Channels", "message": formatted_data_node})
        states.append({"name": "Model Channels", "message": formatted_model_node})
        states.append({"name": "Stages", "message": formatted_stages})
        states.append({"name": "Hyperparameters", "message": self._format_nodes(hyperparameters)})
        states.append({"name": "Environment Variables", "message": self._format_nodes(environment)})

        return states

    def ask_for_requirements_file_name(self):
        """prompt user for image name
        """
        requirements_file_name = click.prompt(
            text=click.style("Set full path to requirements: ", fg='bright_blue'),
            default=self.config.get('requirements_dir', 'requirements.txt')
        )

        self.config.update({
            'requirements_dir':requirements_file_name
        })
    
    def update_stages(self, stages: dict):
        """"""
        self.config.update(
            {'stages': stages}
        )

    def update_env_vars(self, environment: dict):
        """
            Update environment node in .mldock config

            Args:
                environment (dict): key,value dictionaries
        """
        self.config.update(
            {'environment': environment}
        )

    def update_hyperparameters(self, hyperparameters: dict):
        """
            Update hyperparameter node in .mldock config

            Args:
                hyperparameters (dict): key,value dictionaries
        """
        self.config.update(
            {'hyperparameters': hyperparameters}
        )

    def update_data_channels(self, data: dict):
        """
            Update data node in .mldock config

            Args:
                data (dict): key,value dictionaries
        """
        self.config.update(
            {'data': data}
        )
    
    def update_model_channels(self, models: dict):
        """
            Update data node in .mldock config

            Args:
                data (dict): key,value dictionaries
        """
        self.config.update(
            {'model': models}
        )
