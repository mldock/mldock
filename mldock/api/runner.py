from pathlib import Path
from mldock.api.bash import execute_routine
from mldock.platform_helpers.mldock import utils as mldock_utils

def run_script_as_interactive(commands, cwd, env):
    """runs script in interactive mode"""
    # must update /opt/ml working directory before running
    # perhaps setting from environment would be the best
    env.update(
        {
            "MLDOCK_BASE_DIR": Path(cwd).absolute().as_posix(),
            "MLDOCK_INPUT_DIR": ".",
        }
    )

    # subprocess only supports 'ascii' supported str for environment variables
    env = mldock_utils.format_dict_for_subprocess(env)

    execute_routine(
        commands,
        cwd=cwd,
        env=env
    )