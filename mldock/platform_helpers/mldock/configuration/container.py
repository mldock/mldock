"""
    Container Setup Utilities

    Implements workflows based on the environment and GCP specific code to
    download and upload ML assets e.g. Input data, Models and output data
"""
from functools import wraps
import traceback
from pathlib import Path

class BaseTrainingContainer:
    """
        A set of tasks for setup and cleanup of container
    """
    def __init__(self, container_environment, container_logger):
        self.container_logger = container_logger
        self.container_environment = container_environment

    def startup(self):
        """start up tasks executed on a container task setup"""
        self.container_logger.info("Setting up Instance")
        if self.container_environment.environment_variables('MLDOCK_STAGE', default=None) == "prod":
            self.container_logger.info("Env == Prod")
            self.container_environment.setup_inputs()
            self.container_environment.setup_model_artifacts()
        self.container_logger.info("Setup Complete")

    def cleanup(self):
        """clean up tasks executed on container task complete"""
        self.container_logger.info("Running Cleanup Script")
        if self.container_environment.environment_variables('MLDOCK_STAGE', default=None) == "prod":
            self.container_logger.info("Env == Prod")
            self.container_environment.cleanup_model_artifacts()
            self.container_environment.cleanup_outputs()
        self.container_logger.info("Cleanup Complete")

    def wrap(self, function):
        """execution handler for training container worflow"""
        @wraps(function)
        def func_wrapper(*args, **kwargs):
            """
                Wrapper function to decorate function
            """
            try:
                self.startup()
                return function(
                    *args,
                    self.container_environment,
                    self.container_logger,
                    **kwargs
                )
            except Exception as exception:
                # Write out an error file. This will be returned as the failureReason in the
                # DescribeTrainingJob result.
                trc = traceback.format_exc()
                log_file_path = Path(self.container_environment.output_data_dir, 'failure')
                with open(log_file_path, 'w') as file_:
                    file_.write('Exception during training: ' + str(exception) + '\n' + trc)
                # Printing this causes the exception to be in the training job logs, as well.
                self.container_logger.error('Exception during training: ' + str(exception) + '\n' + trc)
                raise
            finally:
                self.cleanup()

        return func_wrapper

class BaseServingContainer:
    """
        A set of tasks for setup and cleanup of container instance and
        between worker starts & completes
    """
    def __init__(self, container_environment, container_logger):
        self.container_environment = container_environment
        self.container_logger = container_logger

    def startup_worker(self):
        """steps to execute when a new worker starts an execution"""
        self.container_logger.info("Worker starting")

    def startup(self):
        """start up tasks executed on a container task setup"""
        self.container_logger.info("Setting up instance")

        if self.container_environment.environment_variables('MLDOCK_STAGE', default=None) == "prod":
            self.container_logger.info("Env == Prod")
            self.container_environment.setup_model_artifacts()
        self.container_logger.info("Setup Complete")

    def cleanup(self):
        """steps to execute when the machine shuts down"""
        # (Optional) instantiate super cleanup to maintain bases functionality
        self.container_logger.info("cleaning instance")

    def cleanup_worker(self):
        """steps to execute when a new worker completes an execution"""
        self.container_logger.info("Worker cleaning")

    def wrap(self, function):
        """execution handler for serving container worflow"""
        @wraps(function)
        def func_wrapper(*args, **kwargs):
            """
                Wrapper function to decorate function
            """
            try:
                self.startup_worker()

                return function(
                    *args,
                    self.container_environment,
                    self.container_logger,
                    **kwargs
                )
            except Exception as exception:
                # Write out an error file. This will be returned as the failureReason in the
                # DescribeTrainingJob result.
                trc = traceback.format_exc()
                log_file_path = Path(self.container_environment.output_data_dir, 'failure')
                with open(log_file_path, 'w') as file_:
                    file_.write('Exception during training: ' + str(exception) + '\n' + trc)
                # Printing this causes the exception to be in the training job logs, as well.
                self.container_logger.error('Exception during training: ' + str(exception) + '\n' + trc)
                raise
            finally:
                self.cleanup_worker()

        return func_wrapper
