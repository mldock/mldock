"""
    Config managers for Configure commands

    Config managers used in command/configure
"""
import sys
import json
import logging
from pathlib import Path
import yaml
import click
from mldock.terminal import ChoiceWithNumbers, style_dropdown
from mldock.config_managers.core import BaseConfigManager
from mldock.platform_helpers import utils

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
        super().__init__()
        self.filepath = filepath

        self.config = self.load_config(self.filepath, create=create)

    def reset(self, config_type):
        """reset given configuration by config key"""
        click.secho("Dropping {} configuration".format(config_type), bg='blue')
        self.config.pop(config_type, None)

    def check_if_exists_else_create(self, file_name: str, create: bool):
        """check that mldock fileexists"""
        if not self.file_exists(file_name):
            if create:
                # deal with possiblity of nested directory
                utils._mkdir(Path(file_name).parents[0])
                # create file
                self.touch(file_name)
            else:
                logger.error((
                    "No MLDOCK CLI config found at '{CONFIG_PATH}/'. "
                    "To create run: 'mldock configure init'".format(
                        CONFIG_PATH=Path(file_name).parents[0]
                    )
                ))
                sys.exit(1)

    def setup_local_config(self):
        """setup and prompt user for local configuration"""
        click.secho("Setup local CLI configuration", bg='blue')
        if self.config.get('local') is None:
            self.config['local'] = {}
        self.ask_for_container_auth_type()
        self.ask_for_environment(config_type='local')

    def setup_templates_config(self):
        """setup and prompt user for templates configuration"""
        click.secho("Setup templates CLI configuration", bg='blue')
        if self.config.get('templates') is None:
            self.config['templates'] = {}
        self.ask_for_template_server()
        self.ask_for_template_root()

    def setup_remotes_config(self):
        """setup and prompt user for templates configuration"""
        click.secho("Setup remotes CLI configuration", bg='blue')
        if self.config.get('remotes') is None:
            self.config['remotes'] = []
        self.ask_for_remote_path()

    def setup_workspace_config(self):
        """setup and prompt user for workspace configuration"""
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
        """
            prompt user for environment variables

            args:
                config_type (str): config key that points to configure config type
        """
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

    def ask_for_remote_path(self):
        """prompt user to set template root
        """

        click.secho("Set remote path", bg='blue', nl=True)

        remote_path = click.prompt(
            text=click.style("Set path to remote: ", fg='bright_blue')
        )

        _, path = utils.get_bucket_and_path_from_scheme(remote_path)
        name = path.replace("/", " ").strip().replace(" ", ":")
        scheme = utils.get_scheme(remote_path)

        remotes_manager = RemotesConfigManager(config=self.config.get('remotes', []))

        remotes_manager.add_remote(
            name=name,
            type=scheme,
            path=remote_path
        )
        self.config['remotes'] = remotes_manager.get_config()

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

    @property
    def remotes(self) -> dict:
        """get config object

        Returns:
            dict: config
        """

        return RemotesConfigManager(
            config=self.config.get('remotes', {})
        )


class PackageConfigManager(BaseConfigManager):
    """Package Requirement Config Manager for sagify
    """

    def __init__(
        self,
        filepath: str,
        create: bool = False
    ):
        super().__init__()
        self.filepath = filepath

        self.config = self.load_config(self.filepath, create=create)

    @staticmethod
    def touch(path):
        """creat an empty txt file

        Args:
            filename (str): path to file
        """
        Path(path).touch()

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
        with path.open() as file_:
            config = file_.readlines()

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
            echo_msg = click.style(
                "Add a development stage. ",
                fg='bright_blue'
            ) + "(Follow the prompts)"

            click.echo(
                echo_msg,
                nl=True
            )

            stage_name = click.prompt(
                text="Stage name: ",
                default="end",
                show_default=False,
                type=str
            )
            if stage_name == "end":
                break

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
    def is_float(value):
        """ Returns True is string is a number. """
        try:
            float(value)
            return True
        except ValueError:
            return False

    def ask_for_hyperparameters(self):
        """prompt user for hyperparameters
        """
        click.secho("Hyperparameters", bg='blue', nl=True)
        while True:

            echo_msg = click.style(
                "Add a hyperparameter. ",
                fg='bright_blue'
            )+"(Follow prompts)"

            click.echo(
                echo_msg,
                nl=True
            )
            hparam_name = click.prompt(
                text="Hyperparameter (name): ",
                default="end",
                show_default=False,
                type=str
            )

            if hparam_name == "end":
                break

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
    def is_float(value):
        """ Returns True is string is a number. """
        try:
            float(value)
            return True
        except ValueError:
            return False

    @staticmethod
    def parse_bool(value):
        """ Returns True is string is a bool. """
        result = value
        if value.lower() == 'true':
            result = True
        elif value.lower() == 'false':
            result = False
        return result

    def ask_for_env_vars(self):
        """prompt user for environment variables
        """
        click.secho("Environment Variables", bg='blue', nl=True)
        while True:
            echo_msg = click.style(
                "Add a environment variable. ",
                fg='bright_blue'
            ) + "(Follow prompts)"

            click.echo(
                echo_msg,
                nl=True
            )

            env_var_name = click.prompt(
                text="Environment Variable (name): ",
                default="end",
                show_default=False,
                type=str
            )
            if env_var_name == "end":
                break

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
        config = {
            Path(dataset['channel'], dataset['filename']).as_posix()
            for dataset in self.config
        }

        config_txt = "\n".join(config) + "\n"

        ignore_filepath = Path(self.base_path,".gitignore")
        Path(ignore_filepath).write_text(config_txt)

    def check_if_asset_exists(self, channel, filename):

        found_match = False
        for i in range(len(self.config)):
            tmp_config = self.config[i]

            if (
                (
                    tmp_config['channel'] == channel
                ) and (
                    tmp_config['filename'] == filename
                )
            ):
                # pop the current config
                found_match = True
        
                return found_match, i
        return False, None
        
    def add_asset(self, update: bool = False, **data_config):
        """add an asset to data config"""


        found_match, i = self.check_if_asset_exists(
            channel=data_config.get('channel'),
            filename=data_config.get('filename')
        )

        if (update==False) and found_match:
            logger.error("dataset artifact already exists. To update, run 'datasets update' instead.")
            exit(0)
        elif update and found_match:
            current_config = self.config.pop(i)
            current_config.update(data_config)
        elif update and (found_match == False):
            logger.error("dataset artifact does not exists. To create, run 'datasets create' instead.")
            exit(0)
        else:
            current_config = data_config

        self.config.append(data_config)

    def remove(self, **data_config):
        found_match, i = self.check_if_asset_exists(
            channel=data_config.get('channel'),
            filename=data_config.get('filename')
        )

        if found_match:
            self.config.pop(i)
        else:
            logger.error("dataset artifact does not exists, so nothing to remove.")

    def get(self, **data_config):
        found_match, i = self.check_if_asset_exists(
            channel=data_config['channel'],
            filename=data_config['filename']
        )

        if found_match:
            return self.config[i]
        else:
            logger.error("dataset artifact does not exists. To create, run 'datasets create' instead.")
            exit(0)

    def ask_for_input_data_channels(self):
        """prompt user for hyperparameters
        """
        click.secho("Input Data Channels", bg='blue', nl=True)
        while True:

            echo_msg = click.style(
                "Add a data channel. ",
                fg='bright_blue'
            ) + "(Expects channel/filename). Hit enter to continue."

            channel_filename_pair = click.prompt(
                text=echo_msg,
                default="end",
                show_default=False,
                type=str
            )

            # pylint: disable=no-else-break
            if channel_filename_pair == "end":

                logger.debug("\nUpdated data channels")

                self.pretty_print()

                break

            elif "/" in channel_filename_pair and channel_filename_pair != 'channel/filename':

                channel, filename = channel_filename_pair.split("/", 1)

                logger.debug((
                    "Adding data/{CHANNEL}/{FILE_NAME}".format(
                        CHANNEL=channel,
                        FILE_NAME=filename
                    )
                ))

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
        config = {
            Path(dataset['channel'], dataset['filename']).as_posix()
            for dataset in self.config
        }

        config_txt = "\n".join(config) + "\n"

        ignore_filepath = Path(self.base_path,".gitignore")
        Path(ignore_filepath).write_text(config_txt)

    def check_if_asset_exists(self, channel, filename):

        found_match = False
        for i in range(len(self.config)):
            tmp_config = self.config[i]

            if (
                (
                    tmp_config['channel'] == channel
                ) and (
                    tmp_config['filename'] == filename
                )
            ):
                # pop the current config
                found_match = True
        
                return found_match, i
        return False, None
        
    def add_asset(self, update: bool = False, **data_config):
        """add an asset to data config"""


        found_match, i = self.check_if_asset_exists(
            channel=data_config.get('channel'),
            filename=data_config.get('filename')
        )

        if (update==False) and found_match:
            logger.error("model artifact already exists. To update, run 'datasets update' instead.")
            exit(0)
        elif update and found_match:
            current_config = self.config.pop(i)
            current_config.update(data_config)
        elif update and (found_match == False):
            logger.error("model artifact does not exists. To create, run 'models create' instead.")
            exit(0)
        else:
            current_config = data_config

        self.config.append(data_config)

    def remove(self, **data_config):
        found_match, i = self.check_if_asset_exists(
            channel=data_config.get('channel'),
            filename=data_config.get('filename')
        )

        if found_match:
            self.config.pop(i)
        else:
            logger.error("model artifact does not exists, so nothing to remove.")

    def get(self, **data_config):
        found_match, i = self.check_if_asset_exists(
            channel=data_config['channel'],
            filename=data_config['filename']
        )

        if found_match:
            return self.config[i]
        else:
            logger.error("model artifact does not exists. To create, run 'models create' instead.")
            exit(0)

    def ask_for_model_channels(self):
        """prompt user for hyperparameters
        """
        click.secho("Model Channels", bg='blue', nl=True)
        while True:

            echo_msg = click.style(
                "Add a model. ",
                fg='bright_blue'
            ) + "(Expects channel/filename). Hit enter to continue."

            channel_filename_pair = click.prompt(
                text=echo_msg,
                default="end",
                show_default=False,
                type=str
            )

            # pylint: disable=no-else-break
            if channel_filename_pair == "end":

                logger.debug("\nUpdated model channels")

                self.pretty_print()

                break

            elif "/" in channel_filename_pair and channel_filename_pair != 'channel/filename':

                channel, filename = channel_filename_pair.split("/", 1)

                logger.debug((
                    "Adding model/{CHANNEL}/{FILE_NAME}".format(
                        CHANNEL=channel,
                        FILE_NAME=filename
                    )
                ))

                self.config.append({
                    'channel': channel,
                    'filename': filename
                })

            else:
                logger.warning("Expected format as channel/filename. Skipping")

class RemotesConfigManager(BaseConfigManager):
    """Remotes Config Manager for mldock
    """
    file_ignores = []
    def __init__(self, config: dict):
        self.config = config

    def check_if_asset_exists(self, name):

        found_match = False
        for i in range(len(self.config)):
            tmp_config = self.config[i]

            if tmp_config['name'] == name:
                # pop the current config
                found_match = True
        
                return found_match, i
        return False, None
        
    def add_remote(self, update: bool = False, **data_config):
        """add an asset to data config"""

        if data_config.get('path', None) is None:
            self.ask_for_remote_path()

        found_match, i = self.check_if_asset_exists(
            name=data_config.get('name')
        )

        if (update==False) and found_match:
            logger.error("remote already exists. Check your .mldock/config file to view and edit remotes.")
            exit(0)
        elif update and found_match:
            current_config = self.config.pop(i)
            current_config.update(data_config)
        elif update and (found_match == False):
            logger.error("remote does not exists. Check your .mldock/config file to view and edit remotes.")
            exit(0)
        else:
            current_config = data_config

        self.config.append(data_config)

    def remove(self, **data_config):
        found_match, i = self.check_if_asset_exists(
            channel=data_config['name']
        )

        if found_match:
            self.config.pop(i)
        else:
            logger.error("remote does not exists. Check your .mldock/config file to view and edit remotes.")

    def get(self, **data_config):
        found_match, i = self.check_if_asset_exists(
            name=data_config['name']
        )

        if found_match:
            return self.config[i]
        else:
            logger.error("remote does not exists. Check your .mldock/config file to view and edit remotes.")
            exit(0)
