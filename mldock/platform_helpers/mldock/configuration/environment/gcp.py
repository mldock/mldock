"""MLDock Friendly Environments for GCP"""
from pathlib import Path
import logging

from mldock.platform_helpers.mldock.configuration.environment import base
from mldock.platform_helpers.gcp.storage import \
    download_input_assets, package_and_upload_model_dir, package_and_upload_output_data_dir

logger = logging.getLogger('mldock')

class GCPEnvironment(base.BaseEnvironment):
    """
        Extends the Environment class to give us
        more specific environment configuration tasks based on
        the GCP resource eco-system.
    """

    def setup_inputs(self):
        """ Iterates and downloads assets remoate -> input channels
        """
        logger.info("getting input assets")
        for channel in self.get_input_channel_iter():

            try:
                download_input_assets(
                    storage_dir_path=channel['value'],
                    local_path=self.input_data_dir,
                    scheme='gs'
                )

            except FileExistsError as exception:
                logger.info("{} Channel skipped. Already exists".format(channel['key']))

    def cleanup_outputs(self):
        """ Iterates and uploads output channel -> remote
        """
        logger.info("pushing outputs to remote")
        for channel in self.get_output_channel_iter():
            # only fetch channels with output
            channel_path = channel['key'].replace("MLDOCK_OUTPUT_CHANNEL_", "").lower()
            local_channel_path = Path(self.output_data_dir, channel_path)
            try:
                package_and_upload_output_data_dir(
                    local_path=local_channel_path,
                    storage_dir_path=channel['value'],
                    scheme='gs'
                )
            except AssertionError as exception:
                logger.info(
                     "Skipping channel. {} is not a "
                     "directory or could not be found".format(
                         local_channel_path
                    )
                )

    def setup_model_artifacts(self):
        """ Iterates and downloads assets remoate -> model channel
        """
        logger.info("getting model assets")
        for channel in self.get_model_input_channel_iter():
            try:
                download_input_assets(
                    storage_dir_path=channel['value'],
                    local_path=self.model_dir,
                    scheme='gs'
                )

            except FileExistsError as exception:
                logger.info("{} Channel skipped. Already exists".format(channel['key']))

    def cleanup_model_artifacts(self):
        """ Iterates and uploads from model channel -> remote
        """
        logger.info("Cleanup Model: {}".format(self.model_dir))

        # only fetch channels with output
        for channel in self.get_model_output_channel_iter():
            channel_path = channel['key'].replace("MLDOCK_MODEL_OUTPUT_CHANNEL_", "").lower()
            local_channel_path = Path(self.model_dir, channel_path)

            try:
                package_and_upload_model_dir(
                    local_path=local_channel_path,
                    storage_dir_path=channel['value'],
                    scheme='gs'
                )
            except AssertionError as exception:
                logger.info(
                     "Skipping channel. {} is not a "
                     "directory or could not be found".format(
                         local_channel_path
                    )
                )
