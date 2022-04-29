import sys
import subprocess
import logging

logger = logging.getLogger("mldock")


def run_script_interactively(cmd, **kwargs):
    """
    Basic runner script for local interactive script execution.

    Supports shell like commands, incl. multiple commands
    """
    output = subprocess.check_output(cmd, shell=True, **kwargs)
    logger.info(output.decode())


def python_executable():
    """Return the real path for the Python executable, if it exists.
    Return RuntimeError otherwise.
    Returns:
        (str): The real path of the current Python executable.
    """
    if not sys.executable:
        raise RuntimeError(
            "Failed to retrieve the real path for the Python executable binary"
        )
    return sys.executable


def execute_commands(commands, cwd=".", env=None):
    run_script_interactively(commands, cwd=cwd, env=env)


def find_and_replace_python_executables(command: str):

    return command.replace("python ", f"{python_executable()} ")


def format_commands(commands: list, delimiter: str = ";"):
    """format list of terminal commands as a shell friendly string delimitered as required"""
    command = f"{delimiter}".join(commands)

    # shell expects single semi-colon
    # as a safety measure, find and replace doubled semi-colon instances
    command = command.replace(";;", ";")

    command = find_and_replace_python_executables(command)

    return command


def execute_routine(commands, cwd=".", env=None):
    """format and execute routine or set of commands"""
    command = format_commands(commands=commands)
    execute_commands(command, cwd=cwd, env=env)
