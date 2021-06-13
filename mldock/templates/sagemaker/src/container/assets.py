import logging
from pathlib import Path
import pandas as pd
from sklearn import datasets

from mldock.platform_helpers.mldock.configuration.environment.sagemaker import SagemakerEnvironment
from mldock.platform_helpers.mldock.configuration.container import \
    BaseTrainingContainer, BaseServingContainer

# Set base logger to INFO
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('mldock')

# Instantiate Environment here
# import to other scripts
environment = SagemakerEnvironment()

# (TODO)
# Assess situations and likelihood of whether users should by
# default create their own or can it be hidden until needed.
# For example, using just the BaseServingContainer by default
# USE-CASES:
#   - special Metric loggers (cleaning up, uploading to separate s3 locatations, etc)
#   - Environment and importing from here to other scripts
class TrainingContainer(BaseTrainingContainer):
    """Implements the base training container, allow a user to override/add/extend any training container setup logic"""
    
    def startup(self):

        super(TrainingContainer, self).startup()
        # in 'dev' we can add the following
        if self.environment.environment_variables('MLDOCK_STAGE', default=None) == "dev":

            # download data
            iris = datasets.load_iris(as_frame=True)
            X = iris.data
            y = iris.target
            # write data to iris input data channel
            pd.concat([X, y], axis=1).to_csv(Path(self.environment.input_data_dir,'iris/train.csv'), index=False)

# (TODO)
# Assess situations and likelihood of whether users should by
# default create their own or can it be hidden until needed.
# For example, using just the BaseServingContainer by default
# USE-CASES:
#   - special Metric loggers (cleaning up, uploading to separate s3 locatations, etc)
#   - Instantiating Environment and importing from here to other scripts
class ServingContainer(BaseServingContainer):
    """Implements the base serving container, allow a user to override/add/extend any serving container setup logic"""
    pass
