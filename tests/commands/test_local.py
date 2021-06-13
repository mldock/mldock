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
            utils._mkdir(dir_path='my_app')
            result = runner.invoke(cli=cli, args=['container','init','--dir', 'my_app','--no-prompt'])
            result = runner.invoke(cli=cli, args=['local','build','--dir','my_app'])

        assert result.exit_code == 0, result.output
