"""Test Container commands"""
import os
from pathlib import Path
from mock import patch
from click.testing import CliRunner
import pytest
import logging
import tempfile
from mldock.__main__ import cli
from mldock.platform_helpers import utils

logger=logging.getLogger('mldock')

@pytest.fixture
def mldock_config_aws():

    return {
        'container_dir': 'container',
        'image_name': 'my_app',
        'mldock_module_dir': 'src',
        'requirements_dir': 'requirements.txt',
        'template': 'generic'
    }

class TestContainerCommands:

    @staticmethod
    @patch(
        'future.moves.subprocess.check_output',
        return_value=None
    )
    def test_command_init_w_no_prompt_runs_successfully(future_output_mock):
        """
            Tests that the init no-prompt command runs successfully.
            Does not test that files are copied correctly.
        """
        runner = CliRunner()

        with tempfile.TemporaryDirectory('my_app') as tmp_dir:

            utils._copy_boilerplate_to_dst(
                src='tests/command/fixtures/base_container',
                dst=tmp_dir,
                remove_first=True
            )

            result = runner.invoke(
                cli=cli,
                args=['configure', 'local'],
                input='2\n\n'
            )
            result = runner.invoke(cli=cli, args=['container', 'init', '--dir', tmp_dir, '--no-prompt'])

        assert result.exit_code == 0, result.output

    @staticmethod
    @patch(
        'future.moves.subprocess.check_output',
        return_value=None
    )
    def test_command_init_w_user_input_runs_successfully(future_output_mock):
        """
            Tests that the init with user input command runs successfully.
            Does not test that files are copied correctly.
        """
        runner = CliRunner()
        with tempfile.TemporaryDirectory('my_app') as tmp_dir:

            utils._copy_boilerplate_to_dst(
                src='tests/command/fixtures/base_container',
                dst=tmp_dir,
                remove_first=True
            )

            result = runner.invoke(
                cli=cli,
                args=['configure', 'local'],
                input='2\n\n'
            )
            result = runner.invoke(
                cli=cli,
                args=['container', 'init', '--dir', tmp_dir],
                input='my_app\ngeneric\nsrc\ncontainer\nrequirements.txt\n\n\n\n\n'
            )

        assert result.exit_code == 0, result.output

    def test_command_init_w_template_no_prompt_runs_successfully(future_output_mock, mldock_config_aws):
        """
            Tests that the init with user input command runs successfully.
            Does not test that files are copied correctly.
        """
        runner = CliRunner()
        # tmp_dir = 'my_app'
        with tempfile.TemporaryDirectory('my_app') as tmp_dir:

            # mldock can't write a new file in tmp directory
            # init an empty file
            mldock_filepath = Path(tmp_dir, 'mldock.json')
            utils._write_json({}, mldock_filepath)

            result = runner.invoke(
                cli=cli,
                args=['configure', 'local'],
                input='2\n\n'
            )
            result = runner.invoke(
                cli=cli,
                args=['container', 'init', '--dir', tmp_dir, '--template', 'generic', '--no-prompt'],
                input='yes\n'
            )

            assert result.exit_code == 0, result.output

            assert mldock_filepath.is_file(), "Failed. No mldock.json was found"

            mldock_config = utils._read_json(mldock_filepath)
            mldock_config_aws.update({'image_name': Path(tmp_dir).relative_to('/tmp').as_posix()})

        assert isinstance(mldock_config.pop('data'), list), "Failed. data was not a list"
        assert isinstance(mldock_config.pop('environment'), dict), "Failed. environment was not a dict"
        assert isinstance(mldock_config.pop('hyperparameters'), dict), "Failed. environment was not a dict"
        assert isinstance(mldock_config.pop('model'), list), "Failed. model was not a list"
        assert isinstance(mldock_config.pop('stages'), dict), "Failed. environment was not a dict"

        assert mldock_config == mldock_config_aws, "Failed. MLDOCK container project config was incorrect"
