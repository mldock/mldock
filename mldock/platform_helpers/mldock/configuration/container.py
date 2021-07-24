"""
    Container Setup Utilities

    Implements workflows based on the environment and GCP specific code to
    download and upload ML assets e.g. Input data, Models and output data
"""
import logging

logger = logging.getLogger('mldock')

class BaseTrainingContainer:
    """
        A set of tasks for setup and cleanup of container
    """
    def __init__(self, environment):
        self.environment = environment

    def startup(self):
        """start up tasks executed on a container task setup"""
        logger.info("\n\n --- Running Startup Script ---")
        if self.environment.environment_variables('MLDOCK_STAGE', default=None) == "prod":
            logger.info("Env == Prod")
            self.environment.setup_inputs()
            self.environment.setup_model_artifacts()
        logger.info("--- Setup Complete --- \n\n")

    def cleanup(self):
        """clean up tasks executed on container task complete"""
        logger.info("\n\n --- Running Cleanup Script ---")
        if self.environment.environment_variables('MLDOCK_STAGE', default=None) == "prod":
            logger.info("Env == Prod")
            self.environment.cleanup_model_artifacts()
            self.environment.cleanup_outputs()
        logger.info("--- Cleanup Complete --- \n\n")

class BaseServingContainer:
    """
        A set of tasks for setup and cleanup of container

        note:
            - Only supports a startup script. Cleanup is a bit fuzzy for serving.
    """
    def __init__(self, environment):
        self.environment = environment

    def startup(self):
        """start up tasks executed on a container task setup"""
        logger.info("\n\n --- Running Startup Script ---")

        if self.environment.environment_variables('MLDOCK_STAGE', default=None) == "prod":
            logger.info("Env == Prod")
            self.environment.setup_model_artifacts()
        logger.info("\n\n --- Setup Complete --- \n\n")

    @staticmethod
    def cleanup():
        """clean up tasks executed on container task complete"""
        logger.info("\n\n --- Running Cleanup Script ---")
        logger.info("\n\n --- No tasks to run --- \n\n")
        logger.info("\n\n --- Cleanup Complete --- \n\n")
