"""Test Mldock Projects cli commands"""
import os
from pathlib import Path
from mock import patch
from click.testing import CliRunner
import pytest
import logging
import tempfile
from mldock.__main__ import cli
from mldock.platform_helpers import utils

logger = logging.getLogger("mldock")


@pytest.fixture
def mldock_config_aws():

    return {
        "container_dir": "container",
        "image_name": "my_app",
        "mldock_module_dir": "src",
        "requirements_dir": "requirements.txt",
        "template": "generic",
        "routines": {
            "deploy": ["python src/container/prediction/serve.py"],
            "train": ["python src/container/training/train.py"],
        },
    }


class TestProjectsCommands:
    @staticmethod
    def test_command_init_w_no_prompt_runs_successfully():
        """
        Tests that the init no-prompt command runs successfully.
        Does not test that files are copied correctly.
        """
        runner = CliRunner()

        with tempfile.TemporaryDirectory() as tmp_dir:

            mldock_project = Path(tmp_dir, "my_app")

            utils._copy_boilerplate_to_dst(
                src="tests/command/fixtures/base_container",
                dst=mldock_project,
                remove_first=True,
            )

            result = runner.invoke(cli=cli, args=["configure", "local"], input="2\n\n")
            result = runner.invoke(
                cli=cli,
                args=["projects", "init", "--dir", mldock_project, "--no-prompt"],
            )

        assert result.exit_code == 0, result.output

    @staticmethod
    def test_command_init_w_user_input_runs_successfully():
        """
        Tests that the init with user input command runs successfully.
        Does not test that files are copied correctly.
        """
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmp_dir:

            mldock_project = Path(tmp_dir, "my_app")

            utils._copy_boilerplate_to_dst(
                src="tests/command/fixtures/base_container",
                dst=mldock_project,
                remove_first=True,
            )

            result = runner.invoke(cli=cli, args=["configure", "local"], input="2\n\n")
            result = runner.invoke(
                cli=cli,
                args=["projects", "init", "--dir", mldock_project],
                input="my_app\ngeneric\nsrc\ncontainer\nrequirements.txt\n\n\n\n\n",
            )

        assert result.exit_code == 0, result.output

    @staticmethod
    def test_command_init_w_template_no_prompt_runs_successfully(mldock_config_aws):
        """
        Tests that the init with user input command runs successfully.
        Does not test that files are copied correctly.
        """
        runner = CliRunner()
        # tmp_dir = 'my_app'
        with tempfile.TemporaryDirectory() as tmp_dir:

            # mldock can't write a new file in tmp directory
            # init an empty file
            mldock_project = Path(tmp_dir, "my_app")
            mldock_filepath = Path(mldock_project, "mldock.yaml")

            result = runner.invoke(cli=cli, args=["configure", "local"], input="2\n\n")
            result = runner.invoke(
                cli=cli,
                args=[
                    "projects",
                    "init",
                    "--dir",
                    mldock_project,
                    "--template",
                    "generic",
                    "--no-prompt",
                ],
                input="yes\n",
            )

            assert result.exit_code == 0, result.output

            assert mldock_filepath.is_file(), "Failed. No mldock.yaml was found"

            mldock_config = utils._read_json(mldock_filepath)
            mldock_config_aws.update({"image_name": "my_app"})

        assert isinstance(
            mldock_config.pop("data"), list
        ), "Failed. data was not a list"
        assert isinstance(
            mldock_config.pop("environment"), dict
        ), "Failed. environment was not a dict"
        assert isinstance(
            mldock_config.pop("hyperparameters"), dict
        ), "Failed. hyperparameters was not a dict"
        assert isinstance(
            mldock_config.pop("model"), list
        ), "Failed. model was not a list"
        assert isinstance(
            mldock_config.pop("stages"), dict
        ), "Failed. stages was not a dict"

        assert (
            mldock_config == mldock_config_aws
        ), "Failed. MLDOCK container project config was incorrect"

    @staticmethod
    def test_command_init_w_template_no_prompt_runs_fails_gracefully(mldock_config_aws):
        """
        Tests that the init with user input command runs successfully.
        Does not test that files are copied correctly.
        """
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmp_dir:

            # mldock can't write a new file in tmp directory
            # init an empty file
            mldock_project = Path(tmp_dir, "my_app")
            mldock_filepath = Path(mldock_project, "mldock.yaml")

            result = runner.invoke(cli=cli, args=["configure", "local"], input="2\n\n")
            result = runner.invoke(
                cli=cli,
                args=[
                    "projects",
                    "init",
                    "--dir",
                    tmp_dir,
                    "--template",
                    "generic",
                    "--no-prompt",
                ],
                input="\n",
            )

            assert result.exit_code == 1, result.output

            assert not mldock_filepath.is_file(), "Failed. A mldock.yaml was found"

    @staticmethod
    def test_command_init_w_template_no_prompt_w_param_runs_successfully(
        mldock_config_aws,
    ):
        """
        Tests that the init with user input command runs successfully.
        Does not test that files are copied correctly.
        """
        runner = CliRunner()

        with tempfile.TemporaryDirectory() as tmp_dir:

            mldock_project = Path(tmp_dir, "my_app")
            mldock_filepath = Path(mldock_project, "mldock.yaml")

            result = runner.invoke(cli=cli, args=["configure", "local"], input="2\n\n")
            result = runner.invoke(
                cli=cli,
                args=[
                    "projects",
                    "init",
                    "--dir",
                    mldock_project,
                    "--template",
                    "generic",
                    "--no-prompt",
                    "-p",
                    "my_param",
                    "value",
                    "-e",
                    "my_var",
                    "value",
                ],
                input="yes\n",
            )

            assert result.exit_code == 0, result.output

            assert mldock_filepath.is_file(), "Failed. No mldock.yaml was found"

            mldock_config = utils._read_json(mldock_filepath)

            mldock_config_aws.update({"image_name": "my_app"})

        assert isinstance(
            mldock_config.pop("data"), list
        ), "Failed. data was not a list"
        assert isinstance(
            mldock_config.pop("model"), list
        ), "Failed. model was not a list"
        assert isinstance(
            mldock_config.pop("stages"), dict
        ), "Failed. stages was not a dict"

        assert mldock_config.pop("environment") == {
            "my_var": "value"
        }, "Failed. environment were not correct."
        assert mldock_config.pop("hyperparameters") == {
            "my_param": "value"
        }, "Failed. hyperparameters were not correct."
        assert (
            mldock_config == mldock_config_aws
        ), "Failed. MLDOCK container project config was incorrect"
