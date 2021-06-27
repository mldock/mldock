import os
import tempfile
from mock import patch
from click.testing import CliRunner

from mldock.__main__ import cli
from mldock.platform_helpers import utils


class TestLocalCommands:

    @staticmethod
    def test_build_successful():
        runner = CliRunner()
        with patch(
                'future.moves.subprocess.check_output',
                return_value=None
        ):
            with tempfile.TemporaryDirectory() as tmp_dir:
                utils._copy_boilerplate_to_dst(src='tests/commands/fixtures/base_container', dst=tmp_dir, remove_first=True)
                result = runner.invoke(cli=cli, args=['container', 'init', '--dir', tmp_dir, '--no-prompt'])

                result = runner.invoke(cli=cli, args=['local', 'build', '--dir', tmp_dir])

        assert result.exit_code == 0, result.output
