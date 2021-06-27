from mock import patch
from click.testing import CliRunner

import logging
import tempfile
from mldock.__main__ import cli
from mldock.platform_helpers import utils

logger=logging.getLogger('mldock')

class TestContainerCommands:

    @staticmethod
    def test_command_init_w_no_prompt_runs_successfully():
        """
            Tests that the init no-prompt command runs successfully.
            Does not test that files are copied correctly.
        """
        runner = CliRunner()
        with patch(
                'future.moves.subprocess.check_output',
                return_value=None
        ):

            with tempfile.TemporaryDirectory('my_app') as tmp_dir:
                utils._copy_boilerplate_to_dst(src='tests/commands/fixtures/base_container', dst=tmp_dir, remove_first=True)

                result = runner.invoke(cli=cli, args=['container', 'init', '--dir', tmp_dir, '--no-prompt'])

        assert result.exit_code == 0, result.output

    @staticmethod
    def test_command_init_w_user_input_runs_successfully():
        """
            Tests that the init with user input command runs successfully.
            Does not test that files are copied correctly.
        """
        runner = CliRunner()
        with patch(
                'future.moves.subprocess.check_output',
                return_value=None
        ):
            with tempfile.TemporaryDirectory('my_app') as tmp_dir:
                utils._copy_boilerplate_to_dst(src='tests/commands/fixtures/base_container', dst=tmp_dir, remove_first=True)
                result = runner.invoke(
                    cli=cli,
                    args=['container', 'init', '--dir', tmp_dir],
                    input='my_app\ngeneric\nsrc\ncontainer\nrequirements.txt\n\n\n\n\n'
                )

        assert result.exit_code == 0, result.output
