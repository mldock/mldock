import os
from pathlib import Path
import tempfile
import logging
import atexit
from pyarrow import fs

from mldock.platform_helpers.mldock.tracking.logging import ExperimentTracker

class TestExperimentTracker:

    @staticmethod
    def __setup_tracker(logger, fs_base_path):

        experiment_tracker = ExperimentTracker(
            logger=logger,
            base_path='test_tracker',
            experiment_name='test_experiment',
            fs_base_path=fs_base_path,
            file_system=fs.LocalFileSystem()
        )
        # temporarily unregister write artifacts from atexit callbacks to test it
        atexit.unregister(experiment_tracker.write_artifacts)
        return experiment_tracker

    def test_logs_written_to_fs_base_path_success(self, caplog):
        """
            Test logs are created and copied to fs_base_path on write_artifacts
        """

        tmp_dir = tempfile.TemporaryDirectory()
        test_dir = Path(tmp_dir.name, "tracker_output").as_posix()
        logger = logging.getLogger(tmp_dir.name)
        logger.setLevel(logging.DEBUG)

        experiment_tracker = self.__setup_tracker(logger, test_dir)
        experiment_tracker.log(r"first log")

        experiment_tracker.write_artifacts()

        files = [path.name for path in Path(test_dir).glob('**/*') if path.is_file()]

        # cleanup
        tmp_dir.cleanup()
        assert files == ['logs.txt', 'manifest.json'], "Failure: Did not create log.txt and manifest.json"

    def test_logs_contain_info_debug_error_success(self, caplog):
        """
            Test logs are created and copied to fs_base_path on write_artifacts
        """

        logger = logging.getLogger("tracker_output")
        logger.setLevel(logging.DEBUG)

        experiment_tracker = self.__setup_tracker(logger, None)
        experiment_tracker.log(r"first log")
        experiment_tracker.log(r"another debug log", level=logging.DEBUG)
        experiment_tracker.log(r"this is a log")
        experiment_tracker.log(r"an error log", level=logging.ERROR)


        for record in caplog.records:
            assert record.levelname in ["INFO", "DEBUG", "ERROR"]

    def test_logs_contain_no_debug_success(self, caplog):
        """
            Test logs are created and copied to fs_base_path on write_artifacts
        """

        logger = logging.getLogger("tracker_output")
        logger.setLevel(logging.INFO)

        experiment_tracker = self.__setup_tracker(logger, None)
        experiment_tracker.log(r"first log")
        experiment_tracker.log(r"another debug log", level=logging.DEBUG)
        experiment_tracker.log(r"this is a log")
        experiment_tracker.log(r"an error log", level=logging.ERROR)


        for record in caplog.records:
            # these should still be logged
            assert record.levelname in ["INFO", "ERROR"]
        for record in caplog.records:
            # these should not be logged
            assert record.levelname not in ["DEBUG"]

    def test_logs_metrics_successful(self, caplog):
        """
            Test logs are created and copied to fs_base_path on write_artifacts
        """

        logger = logging.getLogger("tracker_output")
        logger.setLevel(logging.DEBUG)

        experiment_tracker = self.__setup_tracker(logger, None)
        experiment_tracker.log(r"first log")
        experiment_tracker.log_param('estimators', 5)
        experiment_tracker.log_metric('mae', 0.5)
        experiment_tracker.log(r"another debug log", level=logging.DEBUG)
        experiment_tracker.log_metric('mse', 0.3)
        experiment_tracker.log(r"this is a log")
        experiment_tracker.log_metrics(
            {
                "accuracy": .9,
                "roc": .9
            }
        )
        experiment_tracker.log(r"an error log", level=logging.ERROR)

        metric_logs = []
        for record in caplog.records:
            if "metric:" in record.message:
                metric_logs.append(record.message)
        
        assert len(metric_logs) == 4, "Failure. Metric logs did not match expected"

    def test_logs_params_successful(self, caplog):
        """
            Test logs are created and copied to fs_base_path on write_artifacts
        """

        logger = logging.getLogger("tracker_output")
        logger.setLevel(logging.DEBUG)

        experiment_tracker = self.__setup_tracker(logger, None)
        experiment_tracker.log(r"first log")
        experiment_tracker.log_metric('mae', 0.5)
        experiment_tracker.log(r"another debug log", level=logging.DEBUG)
        experiment_tracker.log(r"this is a log")
        experiment_tracker.log(r"an error log", level=logging.ERROR)
        experiment_tracker.log_param('estimators', 5)
        experiment_tracker.log_params(
            {
                "factors": 10,
                "lr": 0.01
            }
        )

        param_logs = []
        for record in caplog.records:
            if "param:" in record.message:
                param_logs.append(record.message)
        
        assert len(param_logs) == 3, "Failure. Param logs did not match expected"
