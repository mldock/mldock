import logging
from pathlib import Path
import pandas as pd
from sklearn import datasets

from mldock.platform_helpers.mldock.configuration.environment.gcp import GCPEnvironment
from mldock.platform_helpers.mldock.configuration.container import \
    BaseTrainingContainer, BaseServingContainer

# Instantiate Environment here
environment = GCPEnvironment()

# Set debug level
if environment.environment_variables('MLDOCK_LOGS_LEVEL', None) == 'debug':
    log_emit_level=logging.DEBUG
else:
    log_emit_level=logging.INFO

logging.basicConfig(level=log_emit_level)
logger = logging.getLogger('mldock')

# Perform custom assets management tasks
# get data, set up custom requirements for training container, etc
class TrainingContainer(BaseTrainingContainer):
    """
        Implements the base training container,
        allow a user to override/add/extend any training container setup logic
    """
    
    def startup(self):

        # (Optional) instantiate super startup to maintain bases functionality
        super(TrainingContainer, self).startup()

        # add dev stage specific asset management tasks
        if self.environment.environment_variables('MLDOCK_STAGE', default=None) == "dev":

            # download data
            iris = datasets.load_iris(as_frame=True)
            X = iris.data
            y = iris.target
            # write data to iris input data channel
            pd.concat(
                [X, y],
                axis=1
            ).to_csv(
                Path(self.environment.input_data_dir,'iris/train.csv'),
                index=False
            )

class ServingContainer(BaseServingContainer):
    """
        Implements the base serving container,
        allow a user to override/add/extend any training container setup logic.

        A special note:
            - in serving setting, the container life-cycle is tied to a threaded worker.
            - each time a new worker is called, startup() is called.
            - each time a worker completes, cleanup() is called
    """

    def startup_worker(self):

        logger.info("Worker starting")

    def startup(self):

        # (Optional) instantiate super cleanup to maintain bases functionality
        super(ServingContainer, self).startup()

        logger.info("Setting up instance")

    def cleanup_worker(self):

        logger.info("Worker cleaning")

    def cleanup(self):

        # (Optional) instantiate super cleanup to maintain bases functionality
        super(ServingContainer, self).cleanup()

        logger.info("cleaning instance")
