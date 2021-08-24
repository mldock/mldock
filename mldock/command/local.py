"""LOCAL COMMANDS"""
import os
from pathlib import Path
import logging
import click

import sys
import subprocess
import six

from mldock.config_managers.cli import \
    CliConfigureManager
import mldock.api.predict as predict_request
from mldock.terminal import \
    ChoiceWithNumbers, style_dropdown, style_2_level_detail, \
        ProgressLogger, pretty_build_logs
from mldock.platform_helpers.mldock import utils as mldock_utils
from mldock.config_managers.container import MLDockConfigManager
from mldock.api.local import \
    search_mldock_containers, docker_build, train_model, deploy_model

click.disable_unicode_literals_warning = True
logger = logging.getLogger('mldock')
MLDOCK_CONFIG_NAME = 'mldock.json'

class ClientError(Exception):
    """Error class used to separate framework and user errors."""


class _CalledProcessError(ClientError):
    """This exception is raised when a process run by check_call() or
    check_output() returns a non-zero exit status.
    Attributes:
      cmd, return_code, output
    """

    def __init__(self, cmd, return_code=None, output=None):
        self.return_code = return_code
        self.cmd = cmd
        self.output = output
        super(_CalledProcessError, self).__init__()

    def __str__(self):
        if six.PY3 and self.output:
            error_msg = "\n%s" % self.output.decode("latin1")
        elif self.output:
            error_msg = "\n%s" % self.output
        else:
            error_msg = ""

        message = '%s:\nCommand "%s"%s' % (type(self).__name__, self.cmd, error_msg)
        return message.strip()


class InstallModuleError(_CalledProcessError):
    """Error class indicating a module failed to install."""


class InstallRequirementsError(_CalledProcessError):
    """Error class indicating a module failed to install."""


class ImportModuleError(ClientError):
    """Error class indicating a module failed to import."""


class ExecuteUserScriptError(_CalledProcessError):
    """Error class indicating a user script failed to execute."""

def create(cmd, error_class, cwd='.', capture_error=True, **kwargs):
    """Spawn a process with subprocess.Popen for the given command.
    Args:
        cmd (list): The command to be run.
        error_class (cls): The class to use when raising an exception.
        cwd (str): The location from which to run the command (default: None).
            If None, this defaults to the ``code_dir`` of the environment.
        capture_error (bool): Whether or not to direct stderr to a stream
            that can later be read (default: False).
        **kwargs: Extra arguments that are passed to the subprocess.Popen constructor.
    Returns:
        subprocess.Popen: The process for the given command.
    Raises:
        error_class: If there is an exception raised when creating the process.
    """
    try:
        stderr = subprocess.PIPE# if capture_error else None
        print(cmd, cwd, stderr, kwargs.get('env'))
        return subprocess.Popen(
            cmd, cwd=cwd, stderr=stderr, **kwargs
        )
    except Exception as e:  # pylint: disable=broad-except
        six.reraise(error_class, error_class(e), sys.exc_info()[2])

def check_error(cmd, error_class, capture_error=True, **kwargs):
    """Run a commmand, raising an exception if there is an error.
    Args:
        cmd ([str]): The command to be run.
        error_class (cls): The class to use when raising an exception.
        capture_error (bool): Whether or not to include stderr in
            the exception message (default: False). In either case,
            stderr is streamed to the process's output.
        **kwargs: Extra arguments that are passed to the subprocess.Popen constructor.
    Returns:
        subprocess.Popen: The process for the given command.
    Raises:
        error_class: If there is an exception raised when creating the process.
    """
    print(cmd)
    print("start command")
    process = create(cmd, error_class, capture_error=capture_error, **kwargs)
    print("complete -- no listend")
    if capture_error:
        _, stderr = process.communicate()
        # This will force the stderr to be printed after stdout
        # If wait is false and cature error is true, we will never see the stderr.
        print(stderr.decode(errors="replace"))
        return_code = process.poll()
    else:
        stderr = None
        return_code = process.wait()

    if return_code:
        raise error_class(return_code=return_code, cmd=" ".join(cmd), output=stderr)
    return process

@click.group()
def local():
    """
    Commands for local development
    """

@click.command()
@click.option(
    '--project_directory',
    '--dir',
    '-d',
    help='mldock container project.',
    required=True,
    type=click.Path(
        exists=True,
        file_okay=False,
        dir_okay=True,
        writable=True,
        readable=True,
        resolve_path=False,
        allow_dash=False,
        path_type=None
    )
)
@click.option('--no-cache', help='builds container from scratch', is_flag=True)
@click.option('--tag', help='docker tag', type=str, default='latest')
@click.option('--stage', help='environment to stage.')
def build(project_directory, no_cache, tag, stage):
    """Command to build container locally
    """
    mldock_manager = MLDockConfigManager(
        filepath=os.path.join(project_directory, MLDOCK_CONFIG_NAME)
    )
    # get mldock_module_dir name
    mldock_config = mldock_manager.get_config()
    image_name = mldock_config.get("image_name", None)
    template_name = mldock_config.get("template", None)
    container_dir = mldock_config.get("container_dir", None)
    module_path = os.path.join(
        project_directory,
        mldock_config.get("mldock_module_dir", "src"),
    )
    dockerfile_path = os.path.join(
        project_directory,
        mldock_config.get("mldock_module_dir", "src"),
        container_dir,
        "Dockerfile"
    )
    requirements_file_path = os.path.join(
        project_directory,
        mldock_config.get("requirements_dir", "requirements.txt")
    )

    with ProgressLogger(
        group='Stages',
        text='Retrieving Stages',
        spinner='dots',
        on_success='Stages Retrieved'
    ) as spinner:
        stages = mldock_config.get("stages", None)

        if stage is not None:
            tag = stages[stage]['tag']

        if tag is None:
            raise Exception("tag is not valid. Either choose a stage or set a tag manually")

    try:
        with ProgressLogger(group='Build', text='Building', spinner='dots') as spinner:
            logs = docker_build(
                image_name=image_name,
                dockerfile_path=dockerfile_path,
                module_path=module_path,
                target_dir_name=mldock_config.get("mldock_module_dir", "src"),
                requirements_file_path=requirements_file_path,
                no_cache=no_cache,
                docker_tag=tag,
                container_platform=template_name
            )
            for line in logs:

                spinner.info(pretty_build_logs(line=line))

                spinner.start()

    except Exception as exception:
        logger.error(exception)
        raise

@click.command()
@click.option(
    '--payload',
    help='Path to payload',
    required=True,
    type=click.Path(
        exists=True,
        file_okay=True,
        dir_okay=False,
        writable=False,
        readable=True,
        resolve_path=False,
        allow_dash=False,
        path_type=None
    )
)
@click.option(
    '--content-type',
    default='application/json',
    help='format of payload',
    type=click.Choice(
        ['application/json', 'text/csv', 'image/jpeg'],
        case_sensitive=False
    )
)
@click.option(
    '--host',
    help='host url at which model is served',
    type=str,
    default='http://127.0.0.1:8080/invocations'
)
def predict(payload, content_type, host):
    """
    Command to execute prediction request against ml endpoint
    """
    with ProgressLogger(group='Predict', text='Running Request', spinner='dots'):
        if payload is None:
            logger.info("\nPayload cannot be None. Please provide path to payload file.")
        else:
            if content_type in ['application/json']:
                pretty_output = predict_request.send_json(filepath=payload, host=host)
            elif content_type in ['text/csv']:
                pretty_output = predict_request.send_csv(filepath=payload, host=host)
            elif content_type in ['image/jpeg']:
                pretty_output = predict_request.send_image_jpeg(filepath=payload, host=host)
            else:
                raise Exception("Content-type is not supported.")
            logger.info(pretty_output)

@click.command()
@click.option(
    '--project_directory',
    '--dir',
    '-d',
    help='mldock container project.',
    required=True,
    type=click.Path(
        exists=True,
        file_okay=False,
        dir_okay=True,
        writable=True,
        readable=True,
        resolve_path=False,
        allow_dash=False,
        path_type=None
    )
)
@click.option(
    '--params',
    '-p',
    help='(Optional) Hyperparameter override when running container.',
    nargs=2,
    type=click.Tuple([str, str]),
    multiple=True
)
@click.option(
    '--env_vars',
    '-e',
    help='(Optional) Environment Variables override when running container.',
    nargs=2,
    type=click.Tuple([str, str]),
    multiple=True
)
@click.option('--tag', help='docker tag', type=str, default='latest')
@click.option('--stage', help='environment to stage.')
@click.option('--interactive', help='run workflow without docker', is_flag=True)
def train(project_directory, **kwargs):
    """
    Command to run training locally on localhost
    """
    params = kwargs.get('params', None)
    env_vars = kwargs.get('env_vars', None)
    tag = kwargs.get('tag', None)
    stage = kwargs.get('stage', None)
    interactive = kwargs.get('interactive', False)

    mldock_manager = MLDockConfigManager(
        filepath=os.path.join(project_directory, MLDOCK_CONFIG_NAME)
    )
    # get mldock_module_path name
    mldock_config = mldock_manager.get_config()
    image_name = mldock_config.get("image_name", None)

    with ProgressLogger(
        group='Stages',
        text='Retrieving Stages',
        spinner='dots',
        on_success='Stages Retrieved'
    ) as spinner:
        stages = mldock_config.get("stages", None)

        if stage is not None:
            tag = stages[stage]['tag']

        if tag is None:
            raise Exception("tag is not valid. Either choose a stage or set a tag manually")

    with ProgressLogger(
        group='Environment',
        text='Retrieving Environment Varaiables',
        spinner='dots',
        on_success='Environment Ready'
    ) as spinner:
        project_env_vars = mldock_config.get('environment', {})
        for env_var in env_vars:
            key_, value_ = env_var
            project_env_vars.update(
                {key_: value_}
            )

        hyperparameters = mldock_config.get('hyperparameters', {})

        # override hyperparameters
        for param in params:
            key_, value_ = param
            hyperparameters.update(
                {key_: value_}
            )

        env_vars = mldock_utils.collect_mldock_environment_variables(
            stage=stage,
            hyperparameters=hyperparameters,
            **project_env_vars
        )

        config_manager = CliConfigureManager()
        env_vars.update(
            config_manager.local.get('environment', {})
        )

    with ProgressLogger(
        group='Training',
        text='Running Training',
        spinner='dots'
    ) as spinner:

        spinner.info("Training Environment = {}".format(env_vars))
        spinner.start()
        if interactive:
            spinner.info("Running interactively")
            spinner.start()
            # just run python src/container/prediction/serve.py
            base_ml_path = project_directory
            # must update /opt/ml working directory before running
            # perhaps setting from environment would be the best
            env_vars.update({
                'MLDOCK_BASE_DIR': Path(base_ml_path).absolute().as_posix()
            })
            script_path = 'src/container/training/train.py'
            print(script_path)
            process = check_error(
                ["/bin/sh", "-c", "python", script_path],
                ExecuteUserScriptError,
                capture_error=True,
                cwd=base_ml_path,
                env=env_vars
            )
            print(process)
        else:
            spinner.info("Running docker container")
            spinner.start()
            base_ml_path = '/opt/ml'
            train_model(
                working_dir=project_directory,
                docker_tag=tag,
                image_name=image_name,
                entrypoint="src/container/executor.sh",
                cmd="train",
                env=env_vars,
                base_ml_path=base_ml_path
            )


@click.command()
@click.option(
    '--project_directory',
    '--dir',
    '-d',
    help='mldock container project.',
    required=True,
    type=click.Path(
        exists=True,
        file_okay=False,
        dir_okay=True,
        writable=True,
        readable=True,
        resolve_path=False,
        allow_dash=False,
        path_type=None
    )
)
@click.option(
    '--params',
    '-p',
    help='(Optional) Hyperparameter override when running container.',
    nargs=2,
    type=click.Tuple([str, str]),
    multiple=True
)
@click.option(
    '--env_vars',
    '-e',
    help='(Optional) Environment Variables override when running container.',
    nargs=2,
    type=click.Tuple([str, str]),
    multiple=True
)
@click.option('--tag', help='docker tag', type=str, default='latest')
@click.option('--port', help='host url at which model is served', type=str, default='8080')
@click.option('--stage', help='environment to stage.')
@click.option('--interactive', help='run workflow without docker', is_flag=True)
@click.pass_obj
def deploy(obj, project_directory, **kwargs):
    """
    Command to deploy ml container on localhost
    """
    params = kwargs.get('params', None)
    env_vars = kwargs.get('env_vars', None)
    tag = kwargs.get('tag', None)
    port = kwargs.get('port', None)
    stage = kwargs.get('stage', None)
    interactive = kwargs.get('interactive', False)

    verbose = obj.get('verbose', False)
    mldock_manager = MLDockConfigManager(
        filepath=os.path.join(project_directory, MLDOCK_CONFIG_NAME)
    )
    # get mldock_module_path name
    mldock_config = mldock_manager.get_config()
    image_name = mldock_config.get("image_name", None)

    with ProgressLogger(
        group='Stages',
        text='Retrieving Stages',
        spinner='dots',
        on_success='Stages Retrieved'
    ) as spinner:
        stages = mldock_config.get("stages", None)

        if stage is not None:
            tag = stages[stage]['tag']

        if tag is None:
            raise Exception("tag is not valid. Either choose a stage or set a tag manually")

    project_env_vars = mldock_config.get('environment', {})

    for env_var in env_vars:
        key_, value_ = env_var
        print(key_, value_)
        project_env_vars.update(
            {key_: value_}
        )

    hyperparameters = mldock_config.get('hyperparameters', {})

    # override hyperparameters
    for param in params:
        key_, value_ = param
        print(key_, value_)
        hyperparameters.update(
            {key_: value_}
        )

    env_vars = mldock_utils.collect_mldock_environment_variables(
        stage=stage,
        hyperparameters=mldock_config.get('hyperparameters', {}),
        **project_env_vars
    )

    config_manager = CliConfigureManager()
    env_vars.update(
        config_manager.local.get('environment', {})
    )

    with ProgressLogger(
        group='Deploy',
        text='Deploying model to {} @ localhost'.format(port),
        spinner='dots'
    ) as spinner:
        spinner.info("Deployment Environment = {}".format(env_vars))
        spinner.start()
        if interactive:
            spinner.info("Running interactively")
            spinner.start()
            # just run python src/container/prediction/serve.py
            base_ml_path = project_directory
            # must update /opt/ml working directory before running
            # perhaps setting from environment would be the best
            # check out the python runner from sagemaker_training
            env_vars.update({
                'MLDOCK_BASE_DIR': Path(base_ml_path).absolute().as_posix()
            })
            script_path = 'src/container/prediction/serve.py'
            print(script_path)
            process = check_error(
                ["/bin/sh", "-c", "python", script_path],
                ExecuteUserScriptError,
                capture_error=True,
                cwd=base_ml_path,
                env=env_vars
            )
            print(process)
        else:
            spinner.info("Running docker container")
            spinner.start()
            base_ml_path = '/opt/ml'
            deploy_model(
                working_dir=project_directory,
                docker_tag=tag,
                image_name=image_name,
                port={8080: port},
                entrypoint="src/container/executor.sh",
                cmd="serve",
                env=env_vars,
                verbose=verbose,
                base_ml_path=base_ml_path
            )

@click.command()
def stop():
    """
    Command to stop ml container on localhost
    """

    try:
        containers = search_mldock_containers()

        tags = [
            style_2_level_detail(
                major_detail=c.image.tags[0],
                minor_detail=c.name
             ) for c in containers
        ] + ['abort']
        # newline break
        click.echo("")
        click.secho("Running MLDock containers:", bg='blue', nl=True)
        container_tag = click.prompt(
            text=style_dropdown(group_name="container name", options=tags, default='abort'),
            type=ChoiceWithNumbers(tags, case_sensitive=False),
            show_default=False,
            default='abort',
            show_choices=False
        )

        for container in containers:
            for image_tag in container.image.tags:
                if image_tag in container_tag:
                    # make newline
                    click.echo("")
                    project_container_tag = click.style(container_tag, fg='bright_blue')
                    if click.confirm(
                        "Stop the running container = {}?".format(
                            project_container_tag)
                    ):
                        container.kill()

                    break

    except Exception as exception:
        logger.error(exception)
        raise


def add_commands(cli_group: click.group):
    """
        add commands to cli group
        args:
            cli (click.group)
    """
    cli_group.add_command(build)
    cli_group.add_command(predict)
    cli_group.add_command(train)
    cli_group.add_command(deploy)
    cli_group.add_command(stop)

add_commands(local)
