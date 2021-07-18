"""
    Config managers for Configure commands

    Config managers used in command/configure
"""
import os
import json
import yaml
import click
import logging
from pathlib import Path
from appdirs import user_config_dir
from mldock.terminal import ChoiceWithNumbers, style_dropdown
from mldock.config_managers.core import BaseConfigManager

logger = logging.getLogger('mldock')
MLDOCK_CLI_CONFIG="./.mldock/config"

class CliConfigureManager(BaseConfigManager):
    """CLI Configure Manager for mldock
    """

    config = {}

    def __init__(
        self,
        filepath: str = MLDOCK_CLI_CONFIG,
        create: bool = False
    ):
        self.filepath = filepath
        self.config = self.load_config(self.filepath, create=create)

    def reset(self, config_type):
        click.secho("Dropping {} configuration".format(config_type), bg='blue')
        self.config.pop(config_type, None)

    def setup_local_config(self):
        click.secho("Setup local CLI configuration", bg='blue')
        if self.config.get('local') is None:
            self.config['local'] = {}
        self.ask_for_container_auth_type()
        self.ask_for_environment(config_type='local')

    def setup_templates_config(self):
        click.secho("Setup templates CLI configuration", bg='blue')
        if self.config.get('templates') is None:
            self.config['templates'] = {}
        self.ask_for_template_server()
        self.ask_for_template_root()

    def setup_workspace_config(self):
        click.secho("Setup workspace CLI configuration", bg='blue')
        if self.config.get('workspace') is None:
            self.config['workspace'] = {}
        self.ask_for_environment(config_type='workspace')

    def ask_for_container_auth_type(self):
        """prompt user for platform name
        """

        click.secho("Set local authentication type", bg='blue', nl=True)
        options = ['gcloud', 'awscli']

        auth_type = click.prompt(
            text=style_dropdown(
                group_name="authentication type",
                options=options,
                default=self.config.get('auth_type', None)
            ),
            type=ChoiceWithNumbers(options, case_sensitive=False),
            show_default=True,
            default=self.config.get('auth_type', None),
            show_choices=False
        )
        
        self.config['local'].update({
            'auth_type': auth_type
        })

    def ask_for_environment(self, config_type):
        
        config = self.config[config_type].get('environment', {})
        environment_config_manager = EnvironmentConfigManager(config=config)
        environment_config_manager.ask_for_env_vars()
        self.config[config_type].update({
            'environment': environment_config_manager.get_config()
        })
    
    def ask_for_template_server(self):
        """prompt user to set template server tracking
        """

        click.secho("Set template server type", bg='blue', nl=True)
        options = ['local', 'github']

        server_type = click.prompt(
            text=style_dropdown(
                group_name="template server type",
                options=options,
                default=self.config.get('server_type', None)
            ),
            type=ChoiceWithNumbers(options, case_sensitive=False),
            show_default=True,
            default=self.config.get('server_type', None),
            show_choices=False
        )
        
        self.config['templates'].update({
            'server_type': server_type
        })

    def ask_for_template_root(self):
        """prompt user to set template root
        """

        click.secho("Set template root", bg='blue', nl=True)

        templates_root_dir = click.prompt(
            text=click.style("Set path to template root dir: ", fg='bright_blue'),
            default=self.config['templates'].get('templates_root', None)
        )
        
        self.config['templates'].update({
            'templates_root': templates_root_dir
        })

    @staticmethod
    def _format_nodes(config):

        output = []

        for key_ in sorted(config):
            value_ = config[key_]
            if isinstance(value_, dict):
                value_ = yaml.dump(value_, indent=4, sort_keys=True)
            output.append({
                "name": key_, "message": value_
            })

        return output

    def get_state(self):
        """pretty prints a json config to terminal
        """
        config = self.config.copy()

        states = self._format_nodes(config)

        return states

    @property
    def local(self) -> dict:
        """get config object

        Returns:
            dict: config
        """
        return self.config.get('local', {})

    @property
    def workspace(self) -> dict:
        """get config object

        Returns:
            dict: config
        """
        return self.config.get('workspace', {})

    @property
    def templates(self) -> dict:
        """get config object

        Returns:
            dict: config
        """
        return self.config.get('templates', {})

class ResourceConfigManager(BaseConfigManager):
    """Resource Config Manager for mldock
    """
    config = {
        "current_host": "algo-1",
        "hosts": [
            "algo-1"
        ],
        "network_interface_name": "eth1"
    }

    @staticmethod
    def ask_for_current_host_name():
        """prompt user for current host name

        Returns:
            return: current host name
        """
        current_host_name = chosen_python_index = click.prompt(
            text="Set current host name: ",
            default="algo",
        )

        return current_host_name

    @staticmethod
    def ask_for_network_interface_name():
        """prompt user for network interface name

        Returns:
            str: network interface name
        """
        network_interface_name = click.prompt(
            text="Set current host name: ",
            default="eth1",
        )

        return network_interface_name

    def ask_for_resourceconfig(self):
        """prompt user for resource config
        """
        current_host_name = self.ask_for_current_host_name()
        hosts = [current_host_name+"-1"]
        network_interface_name = self.ask_for_network_interface_name()

        self.config = {
            "current_host": hosts[0],
            "hosts": hosts,
            "network_interface_name": network_interface_name
        }

class PackageConfigManager(BaseConfigManager):
    """Package Requirement Config Manager for sagify
    """
    @staticmethod
    def touch(filename):
        """creat an empty txt file

        Args:
            filename (str): path to file
        """
        Path(filename).touch()

    def load_config(self, file_name: str, create: bool) -> list:
        """load config

        Args:
            filename (str): path to config file to load

        Returns:
            list: config
        """
        self.check_if_exists_else_create(
            file_name=file_name, create=create
        )
        path = Path(file_name)
        with path.open() as f: 
            config = f.readlines()
        
        for index, c_package in enumerate(config):
            if c_package.endswith("\n"):
                config[index] = config[index].split("\n")[0]
        return config

    def get_config(self) -> list:
        """get config object

        Returns:
            list: config
        """
        return self.config

    def seed_packages(self, packages: list):
        """seeds config with required package modules

        Args:
            packages (list): packages to add to config
        """
        for new_package in packages:
            for config_package in self.config:
                if new_package not in config_package:
                    self.config.append(new_package)

    def pretty_print(self):
        """pretty prints a list config to terminal
        """
        pretty_config = json.dumps(self.config, indent=4, separators=(',', ': '))
        logger.debug("{}\n".format(pretty_config))

    def write_file(self):
        """
        write to file
        """
        config = set(self.config)
        config_txt = "\n".join(config) + "\n"
        Path(self.filepath).write_text(config_txt)

class StageConfigManager(BaseConfigManager):
    """Development Stage Config Manager for mldock
    """

    def __init__(self, config: dict):
        self.config = config

    def ask_for_stages(self):
        """prompt user for stages
        """
        click.secho("Stages", bg='blue', nl=True)
        while True:
            click.echo(click.style("Add a development stage. ", fg='bright_blue')+"(Follow the prompts)", nl=True)
            stage_name = click.prompt(
                text="Stage name: ",
                default="end",
                show_default=False,
                type=str
            )
            if stage_name == "end":
                break
            else:
                docker_tag = click.prompt(
                    text="Set docker image tag: ",
                    default=self.config.get(stage_name, {}).get('tag', None)
                )
                if stage_name not in self.config:
                    self.config[stage_name] = {}

                self.config[stage_name].update(
                    {'tag': docker_tag}
                )

class HyperparameterConfigManager(BaseConfigManager):
    """Hyperparameter Config Manager for mldock
    """

    def __init__(self, config: dict):
        self.config = config

    @staticmethod
    def is_float(s):
        """ Returns True is string is a number. """
        try:
            float(s)
            return True
        except ValueError:
            return False

    def ask_for_hyperparameters(self):
        """prompt user for hyperparameters
        """
        click.secho("Hyperparameters", bg='blue', nl=True)
        while True:
            click.echo(click.style("Add a hyperparameter. ", fg='bright_blue')+"(Follow prompts)", nl=True)
            hparam_name = click.prompt(
                text="Hyperparameter (name): ",
                default="end",
                show_default=False,
                type=str
            )
            if hparam_name == "end":
                break
            else:
                hparam_value = click.prompt(
                    text="Set value: ",
                    default=self.config.get(hparam_name, None)
                )

                self.config.update(
                    {hparam_name: hparam_value}
                )

class EnvironmentConfigManager(BaseConfigManager):
    """Environment Config Manager for mldock
    """
    def __init__(self, config: dict):
        self.config = config

    @staticmethod
    def is_float(s):
        """ Returns True is string is a number. """
        try:
            float(s)
            return True
        except ValueError:
            return False

    @staticmethod
    def parse_bool(s):
        """ Returns True is string is a bool. """
        if s.lower() == 'true':
            return True
        elif s.lower() == 'false':
            return False
        else:
            return s

    def ask_for_env_vars(self):
        """prompt user for environment variables
        """
        click.secho("Environment Variables", bg='blue', nl=True)
        while True:
            click.echo(click.style("Add a environment variable. ", fg='bright_blue')+"(Follow prompts)", nl=True)
            env_var_name = click.prompt(
                text="Environment Variable (name): ",
                default="end",
                show_default=False,
                type=str
            )
            if env_var_name == "end":
                break
            else:
                env_var_value = click.prompt(
                    text="Set value: ",
                    default=self.config.get(env_var_name, None)
                )

                self.config.update(
                    {env_var_name: env_var_value}
                )

class InputDataConfigManager(BaseConfigManager):
    """InputData Config Manager for mldock
    """
    file_ignores = []
    def __init__(self, config: dict, base_path: str):
        self.config = config
        self.base_path = base_path

    def write_gitignore(self):
        """
        write to file
        """
        config = set([Path(dataset['channel'], dataset['filename']).as_posix() for dataset in self.config])
        config_txt = "\n".join(config) + "\n"

        ignore_filepath = Path(self.base_path,".gitignore")
        Path(ignore_filepath).write_text(config_txt)

    def ask_for_input_data_channels(self):
        """prompt user for hyperparameters
        """
        click.secho("Input Data Channels", bg='blue', nl=True)
        while True:
            channel_filename_pair = click.prompt(
                text=click.style("Add a data channel. ", fg='bright_blue')+"(Expects channel/filename). Hit enter to continue.",
                default="end",
                show_default=False,
                type=str
            )
            if channel_filename_pair == "end":
                logger.debug("\nUpdated data channels")
                self.pretty_print()
                break
            elif "/" in channel_filename_pair and not channel_filename_pair == "channel:filename":
                channel, filename = channel_filename_pair.split("/",1)
                logger.debug("Adding data/{}/{}".format(channel, filename))
                self.config.append({
                    'channel': channel,
                    'filename': filename
                })
            else:
                logger.warning("Expected format as channel/filename. Skipping")

class ModelConfigManager(BaseConfigManager):
    """Model Config Manager for mldock
    """
    file_ignores = []
    def __init__(self, config: dict, base_path: str):
        self.config = config
        self.base_path = base_path

    def write_gitignore(self):
        """
        write to file
        """
        config = set([Path(dataset['channel'], dataset['filename']).as_posix() for dataset in self.config])
        config_txt = "\n".join(config) + "\n"

        ignore_filepath = Path(self.base_path,".gitignore")
        Path(ignore_filepath).write_text(config_txt)

    def ask_for_model_channels(self):
        """prompt user for hyperparameters
        """
        click.secho("Model Channels", bg='blue', nl=True)
        while True:
            channel_filename_pair = click.prompt(
                text=click.style("Add a model channel. ", fg='bright_blue')+"(Expects channel/filename). Hit enter to continue.",
                default="end",
                show_default=False,
                type=str
            )
            if channel_filename_pair == "end":
                logger.debug("\nUpdated model channels")
                self.pretty_print()
                break
            elif "/" in channel_filename_pair and not channel_filename_pair == "channel:filename":
                channel, filename = channel_filename_pair.split("/",1)
                logger.debug("Adding data/{}/{}".format(channel, filename))
                self.config.append({
                    'channel': channel,
                    'filename': filename
                })
            else:
                logger.warning("Expected format as channel/filename. Skipping")
