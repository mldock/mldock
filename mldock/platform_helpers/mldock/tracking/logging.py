"""LOGGING-BASED MLDOCK TRACKER COMPONENTS"""
import atexit
import io
import uuid
import warnings
import logging
from pathlib import Path
import tempfile
from pyarrow import fs

from mldock.platform_helpers import utils

logger = logging.getLogger('mldock')
logger.setLevel(logging.INFO)

class ExperimentTracker:
    """
        Experiment Tracker that supports logging metrics
        and params. Finally, uploading to remote on exit if fs_base_path is provided
    """
    metrics: dict = None
    params: dict = None

    def __init__(self, experiment_name, experiment_logger, file_system, **kwargs):

        self.file_system = file_system
        self.fs_base_path = kwargs.get('fs_base_path', None)
        self.base_path = kwargs.get('base_path', '.')
        self.manifest = kwargs.get('manifest', {})

        self.experiment_name = experiment_name
        self.run_id = str(uuid.uuid4())

        self.experiment_logger = experiment_logger
        # use a certain type of StreamHandler
        self.buffer = io.StringIO()
        stream_handler = logging.StreamHandler(self.buffer)

        # pytest: disable=R1732
        self.tmp_dir = tempfile.TemporaryDirectory(suffix=None, prefix=None, dir=None)
        self.artifact_dir = Path(
            self.tmp_dir.name,
            self.base_path,
            self.experiment_name,
            self.run_id
        )
        Path(self.artifact_dir).mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(Path(self.artifact_dir, 'logs.txt'), mode='a')

        # add it to experiment_logger
        self.experiment_logger.addHandler(stream_handler)
        self.experiment_logger.addHandler(file_handler)

        self.metrics = {}
        self.params = {}

        # register write_artifacts to fire on script exit.
        atexit.register(self.write_artifacts)

    def log(self, msg, *args, **kwargs):
        """log message to log stream"""

        level = kwargs.get('level', logging.INFO)
        self.experiment_logger.log(level, msg, *args, **kwargs)

    def log_metric(self, name, value):
        """log a metric to log stream"""
        self.metrics.update(
            {name: value}
        )
        msg = "metric: {NAME}={VALUE};".format(NAME=name, VALUE=value)
        self.log(msg)

    def log_metrics(self, metrics: dict):
        """log metrics to log stream"""
        self.metrics.update(
            metrics
        )
        for name, value in metrics.items():
            self.log_metric(name, value)

    def log_param(self, name, value):
        """log a param to log stream"""
        self.params.update(
            {name: value}
        )
        msg = "param: {NAME}={VALUE};".format(NAME=name, VALUE=value)
        self.log(msg)

    def log_params(self, params: dict):
        """log params to log stream"""
        self.params.update(
            params
        )
        for name, value in params.items():
            self.log_param(name, value)

    def upload_assets(self, fs_base_path):
        """Uploads logs to specified file-system"""
        # strip the scheme if it is provided
        fs_base_path = utils.strip_scheme(fs_base_path)

        # create full artifacts base path
        artifacts_base_path = Path(
            fs_base_path,
            self.base_path,
            self.experiment_name,
            self.run_id
        )

        local = fs.LocalFileSystem()

        file_selector = fs.FileSelector(
            self.artifact_dir.as_posix(),
            recursive=True
        )
        for file in local.get_file_info(file_selector):
            src_path = Path(file.path)
            file_name = src_path.name
            dst_path = Path(artifacts_base_path, file_name)

            if isinstance(self.file_system, fs.LocalFileSystem):
                artifacts_base_path.mkdir(parents=True, exist_ok=True)
                self.file_system.copy_file(src_path.as_posix(), dst_path.as_posix())
            else:
                self.file_system.upload(src_path.as_posix(), dst_path.as_posix())

    def write_metadata(self):
        """write metadata file to experiment tmp location"""
        self.manifest.update(
            {
                "params": self.params,
                "metrics": self.metrics
            }
        )
        utils._write_json(
            obj=self.manifest,
            file_path=Path(self.artifact_dir, 'manifest.json')
        )

    def write_artifacts(self):
        """Write experiment artifacts"""
        try:
            if self.fs_base_path is None:
                warnings.warn(
                    "Skipping syncronization of run = '{RUN}' for experiment = '{EXPERIMENT}'. "
                    "To syncronize set 'fs_base_path' to "
                    "either local filepath, s3 or gs.".format(
                        EXPERIMENT=self.experiment_name,
                        RUN=self.run_id
                    )
                )
            else:
                # writes the final metadata file
                self.write_metadata()

                # upload assets to file-system
                self.upload_assets(fs_base_path=self.fs_base_path)
        except Exception as exception:
            raise "Failed to write artifacts" from exception
        finally:
            self.tmp_dir.cleanup()
