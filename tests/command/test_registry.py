"""Test registry cli commands"""
from pathlib import Path
import tempfile
from mock import patch
from click.testing import CliRunner

from mldock.__main__ import cli
from mldock.platform_helpers import utils


class TestRegistryCommands:
    """Test Registry cli commands"""
    @staticmethod
    @patch('mldock.command.registry.login_and_authenticate', return_value=(None, {"repository": None}))
    @patch('mldock.command.registry.docker_build')
    @patch('mldock.command.registry.push_image_to_repository')
    def test_push_build_gets_correct_requirements_from_config(
        push_image_mock,
        docker_build_mock,
        docker_auth_mock
    ):
        """test build get's correct requirements from config"""
        runner = CliRunner()

        with tempfile.TemporaryDirectory() as tmp_dir:
            utils._copy_boilerplate_to_dst(src='tests/command/fixtures/base_container', dst=tmp_dir, remove_first=True)
            mldock_config = utils._read_json("tests/command/fixtures/base_container/mldock.json")
            _ = runner.invoke(cli=cli, args=['container', 'init', '--dir', tmp_dir, '--no-prompt'])

            _ = runner.invoke(
                cli=cli,
                args=[
                    'registry',
                    'push',
                    '--dir',
                    tmp_dir,
                    '--build',
                    '--provider',
                    'dockerhub',
                    '--region',
                    None
                ]
            )

            _, kwargs = docker_build_mock.call_args
            requirements_path = Path(kwargs['requirements_file_path']).relative_to(tmp_dir).as_posix()

            assert requirements_path == mldock_config["requirements_dir"], (
                "Failed to get correct requirements directory for build"
            )
