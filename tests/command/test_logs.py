"""Test local cli commands"""
import collections
import uuid
from pathlib import Path
import tempfile
import pytest
from mock import patch
from click.testing import CliRunner

from mldock.__main__ import cli
from mldock.platform_helpers import utils

@pytest.fixture
def log_data():

    return (
        "Experiment id = landing_page_forecaster\n"
        "param: train:ESTIMATORS=10;\n"
        "param: test#iterations=5;\n"
        "Running Evaluation\n"
        "metric: train:accuracy=0.9666666666666667;\n"
        "metric: test~accuracy=0.9;\n"
        "Refitting Final Model"
    )


class TestLocalCommands:
    """Test local cli commmands"""

    @staticmethod
    def __create_textfile(my_path, log_data):
        """creates textfile and seeds it with msg"""
        # This currently assumes the path to the file exists.
        with open(my_path, 'w+') as file:
            file.write(log_data)

    @patch('mldock.command.logs.metrics.print_table')
    def test_logs_metrics_grok_successful(self, mock_print_table, log_data):
        """test logs metrics groks logs as aspected"""
        runner = CliRunner()

        # create tmp directory
        tmp_dir = tempfile.TemporaryDirectory()

        # create tmp experiment dir
        tmp_experiment_dir = Path(tmp_dir.name, str(uuid.uuid4()))
        tmp_experiment_dir.mkdir(parents=True, exist_ok=True)

        # create textfile of logs
        txtfile = Path(tmp_experiment_dir, 'logs.txt').as_posix()
        self.__create_textfile(txtfile, log_data=log_data)

        # run CLI command
        result = runner.invoke(
            cli=cli,
            args=['logs', 'metrics', 'show', '--log-path', tmp_dir.name]
        )

        # mock print_table and get args it was passed
        args, _ = mock_print_table.call_args
        validation = {'experiment', 'test~accuracy', 'run_id', 'train:accuracy'}

        assert args[0] == validation, "Failed to parse metric names correctly"
        assert result.exit_code == 0, result.output

    @patch('mldock.command.logs.params.print_table')
    def test_logs_params_grok_successful(self, mock_print_table, log_data):
        """test logs params groks logs as aspected"""
        runner = CliRunner()

        # create tmp directory
        tmp_dir = tempfile.TemporaryDirectory()

        # create tmp experiment dir
        tmp_experiment_dir = Path(tmp_dir.name, str(uuid.uuid4()))
        tmp_experiment_dir.mkdir(parents=True, exist_ok=True)

        # create textfile of logs
        txtfile = Path(tmp_experiment_dir, 'logs.txt').as_posix()
        self.__create_textfile(txtfile, log_data=log_data)

        # run CLI command
        result = runner.invoke(
            cli=cli,
            args=['logs', 'params', 'show', '--log-path', tmp_dir.name]
        )

        # mock print_table and get args it was passed
        args, _ = mock_print_table.call_args
        validation = {'test#iterations', 'experiment', 'run_id', 'train:ESTIMATORS'}

        assert args[0] == validation, "Failed to parse param names correctly"
        assert result.exit_code == 0, result.output
