"""MLDock Friendly Environments for Sagemaker"""
from pathlib import Path
from mldock.platform_helpers.mldock.configuration.environment import base
from mldock.platform_helpers.aws.sagemaker.environment import \
    Environment as BaseSagemakerEnvironment

class SagemakerEnvironment(BaseSagemakerEnvironment, base.AbstractEnvironment):
    """
        Structures Sagemaker Environment similarily to
        other environments maintaining it's function
    """
    def __init__(self, **kwargs):
        super().__init__()
        del kwargs

    @property
    def input_data_dir(self):
        """
            Input data directory where channels are stored.

            Note:
                - this extends the sagemaker API to the standard mldock API.
        """
        return Path(self.input_dir, 'data')
