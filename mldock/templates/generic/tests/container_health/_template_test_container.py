import os
import sys
import time
from click.testing import CliRunner
import pytest
from serum.__main__ import cli
from serum.api.local import local_deploy_detached

class TestContainerHealth:

    project_dir=/add/you/project/dir/here

    cli_dir='--dir={PROJECT_DIR}'.format(PROJECT_DIR=project_dir)

    def test_container_build_success(self, capsys):
        """Test container builds successfull
        """
        runner = CliRunner()

        result = runner.invoke(cli=cli, args=['local', 'build', self.cli_dir])

        assert result.exit_code == 0
        assert "Build Complete! ヽ(´▽`)/" in result.output

    def test_container_run_train_success(self, capsys):
        """Test container runs training successfully
        """
        runner = CliRunner()

        result = runner.invoke(cli=cli, args=['local', 'train', self.cli_dir])

        assert result.exit_code == 0
        assert "Training Complete! ヽ(´▽`)/" in result.output

    def test_container_run_deploy_success(self, capsys):
        """Test container runs deploy successfully
        """
        runner = CliRunner()

        result = runner.invoke(cli=cli, args=['local', 'deploy', self.cli_dir])

        assert result.exit_code == 0
        assert "Deploy Ready! ヽ(´▽`)/" in result.output
