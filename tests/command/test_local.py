"""Test local cli commands"""
from pathlib import Path
import tempfile
from mock import patch
from click.testing import CliRunner

from mldock.__main__ import cli
from mldock.platform_helpers import utils


class TestLocalCommands:
    """Test local cli commmands"""
    @staticmethod
    @patch(
        'future.moves.subprocess.check_output',
        return_value=None
    )
    def test_build_successful(future_output_mock):
        """test build runs as aspected"""
        runner = CliRunner()

        with tempfile.TemporaryDirectory() as tmp_dir:

            utils._copy_boilerplate_to_dst(
                src='tests/command/fixtures/base_container',
                dst=tmp_dir,
                remove_first=True
            )

            result = runner.invoke(
                cli=cli,
                args=['configure', 'local'],
                input='\n\n\n'
            )
            _ = runner.invoke(cli=cli, args=['container', 'init', '--dir', tmp_dir, '--no-prompt'])

            result = runner.invoke(cli=cli, args=['local', 'build', '--dir', tmp_dir])

        assert result.exit_code == 0, result.output

    @staticmethod
    @patch('mldock.command.local.docker_build')
    @patch(
        'future.moves.subprocess.check_output',
        return_value=None
    )
    def test_build_gets_correct_requirements_from_config(future_output_mock, docker_build_mock):
        """test build get's correct requirements from config"""
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmp_dir:

            utils._copy_boilerplate_to_dst(
                src='tests/command/fixtures/base_container',
                dst=tmp_dir,
                remove_first=True
            )

            mldock_config = utils._read_json("tests/command/fixtures/base_container/mldock.json")

            result = runner.invoke(
                cli=cli,
                args=['configure', 'local'],
                input='\n\n\n'
            )
            _ = runner.invoke(cli=cli, args=['container', 'init', '--dir', tmp_dir, '--no-prompt'])

            _ = runner.invoke(cli=cli, args=['local', 'build', '--dir', tmp_dir])

            _, kwargs = docker_build_mock.call_args
            requirements_path = Path(kwargs['requirements_file_path']).relative_to(tmp_dir).as_posix()

            assert requirements_path == mldock_config["requirements_dir"], (
                "Failed to get correct requirements directory for build"
            )
