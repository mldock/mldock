"""MLDock Friendly Environments for AWS"""
from pathlib import Path
import logging
import s3fs

from mldock.platform_helpers.mldock.configuration.environment import base
# from mldock.platform_helpers.aws.storage import \
#     download_input_assets, package_and_upload_model_dir, package_and_upload_output_data_dir
from mldock.platform_helpers.mldock.storage.pyarrow import download_assets, upload_assets
from mldock.platform_helpers import utils

logger = logging.getLogger('mldock')

class AWSEnvironment(base.BaseEnvironment):
    """
        Extends the Environment class to give us
        more specific environment configuration tasks based on
        the AWS resource eco-system.
    """

    def setup_inputs(self):
        """ Iterates and downloads assets remoate -> input channels
        """
        logger.debug((
            "Setup assets in {INPUT_DATA_DIR}".format(
                INPUT_DATA_DIR=self.input_data_dir
            )
        ))
        # only fetch channels of environment prefix MLDOCK_INPUT_CHANNEL_
        channels = self.get_input_channel_iter()

        if len(channels) == 0:
            logger.debug("No input channels were found in ENV VARS.")

        for channel in channels:
            channel_path = channel['key'].replace("MLDOCK_INPUT_CHANNEL_", "").lower()
            local_channel_path = Path(self.input_data_dir, channel_path)
            try:
                path_without_scheme = utils.strip_scheme(channel['value'])
                file_system = s3fs.S3FileSystem()
                download_assets(
                    file_system,
                    fs_base_path=path_without_scheme,
                    local_path=local_channel_path,
                    storage_location='.'
                )

            except FileExistsError:
                logger.debug((
                    "{CHANNEL_KEY} Channel skipped. "
                    "Already exists".format(CHANNEL_KEY=channel['key'])
                ))

    def cleanup_outputs(self):
        """ Iterates and uploads output channel -> remote
        """
        logger.debug((
            "Cleanup assets in {OUTPUT_DATA_DIR}".format(
                OUTPUT_DATA_DIR=self.output_data_dir
            )
        ))
        # only fetch channels of environment prefix MLDOCK_OUTPUT_CHANNEL_
        channels = self.get_output_channel_iter()

        if len(channels) == 0:
            logger.debug("No output channels were found in ENV VARS.")

        for channel in channels:
            # only fetch channels with output
            channel_path = channel['key'].replace("MLDOCK_OUTPUT_CHANNEL_", "").lower()
            local_channel_path = Path(self.output_data_dir, channel_path)
            try:

                path_without_scheme = utils.strip_scheme(channel['value'])
                file_system = s3fs.S3FileSystem()
                upload_assets(
                    file_system,
                    fs_base_path=path_without_scheme,
                    local_path=local_channel_path,
                    storage_location='.',
                    zip=True
                )

            except AssertionError:
                logger.debug(
                    "Skipping channel. {LOCAL_CHANNEL_PATH} is not a "
                    "directory or could not be found".format(
                        LOCAL_CHANNEL_PATH=local_channel_path
                    )
                )

    def setup_model_artifacts(self):
        """ Iterates and downloads assets remoate -> model channel
        """
        logger.debug("Setup model assets in {MODEL_DIR}".format(MODEL_DIR=self.model_dir))
        # only fetch channels of environment prefix MLDOCK_MODEL_INPUT_CHANNEL_
        channels = self.get_model_input_channel_iter()

        if len(channels) == 0:
            logger.debug("No input channels were found in ENV VARS.")

        for channel in channels:

            channel_path = channel['key'].replace("MLDOCK_MODEL_INPUT_CHANNEL_", "").lower()
            local_channel_path = Path(self.model_dir, channel_path)
            try:
                path_without_scheme = utils.strip_scheme(channel['value'])
                file_system = s3fs.S3FileSystem()
                download_assets(
                    file_system,
                    fs_base_path=path_without_scheme,
                    local_path=local_channel_path,
                    storage_location='.'
                )

            except FileExistsError:
                logger.debug((
                    "{CHANNEL_KEY} Channel skipped. Already exists".format(
                        CHANNEL_KEY=channel['key']
                    )
                ))

    def cleanup_model_artifacts(self):
        """ Iterates and uploads from model channel -> remote
        """
        logger.debug((
            "Cleanup model assets in {MODEL_DIR}".format(
                MODEL_DIR=self.model_dir
            )
        ))

        # only fetch channels of environment prefix MLDOCK_MODEL_OUTPUT_CHANNEL_
        channels = self.get_model_output_channel_iter()

        if len(channels) == 0:
            logger.debug("No model channels were found in ENV VARS.")

        for channel in channels:
            channel_path = channel['key'].replace("MLDOCK_MODEL_OUTPUT_CHANNEL_", "").lower()
            local_channel_path = Path(self.model_dir, channel_path)

            try:
                path_without_scheme = utils.strip_scheme(channel['value'])
                file_system = s3fs.S3FileSystem()
                upload_assets(
                    file_system,
                    fs_base_path=path_without_scheme,
                    local_path=local_channel_path,
                    storage_location='.',
                    zip=True
                )

            except AssertionError:
                logger.debug(
                    "Skipping channel. {LOCAL_CHANNEL_PATH} is not a "
                    "directory or could not be found".format(
                        LOCAL_CHANNEL_PATH=local_channel_path
                    )
                )
