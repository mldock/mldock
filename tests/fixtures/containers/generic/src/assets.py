"""
    CONTAINER ASSETS MANAGEMENT

    Provides class objects with methods to execute at certain parts of the container life-cycle, i.e. startup or cleanup, etc.
    In short we call them TrainingContainer and ServingContainer classes. Each provides everything your container needs, including
    environment, logger, etc.
    Since Serving Containers and Training Containers are unique in use-case and requirements, we recommend providing one for each workflow.
"""
from pathlib import Path
import pandas as pd
from sklearn import datasets
from mldock.platform_helpers.mldock.configuration.container import (
    BaseServingContainer,
    BaseTrainingContainer,
)

# Training Container Assets Management
class TrainingContainer(BaseTrainingContainer):
    """
    Implements the base training container,
    allow a user to override/add/extend any training container setup logic
    """

    def __init__(self, **kwargs):
        super(TrainingContainer, self).__init__(**kwargs)

    def startup(self):
        """steps to execute when the machine starts up"""
        # (Optional) instantiate super startup to maintain bases functionality
        super(TrainingContainer, self).startup()
        # add dev stage specific asset management tasks
        if (
            self.container_environment.environment_variables(
                "MLDOCK_STAGE", default=None
            )
            == "dev"
        ):

            # create channel if it doesn't exist
            data_channel = Path(self.container_environment.input_data_dir, "iris")
            data_channel.mkdir(parents=True, exist_ok=True)

            # download data
            iris = datasets.load_iris(as_frame=True)
            X = iris.data
            y = iris.target

            # write data to iris input data channel
            pd.concat([X, y], axis=1).to_csv(
                Path(data_channel, "train.csv"), index=False
            )


# Serving Container Assets Management
class ServingContainer(BaseServingContainer):
    """
    Implements the base serving container,
    allow a user to override/add/extend any training container setup logic.
    """
    pass

