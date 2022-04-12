from pathlib import Path
import logging
from pyarrow import fs

from mldock.platform_helpers.mldock.configuration.environment import base
from mldock.platform_helpers.mldock.storage.pyarrow import (
    download_assets,
    upload_assets,
)
from mldock.platform_helpers import utils

logger = logging.getLogger("mldock")

class BaseEnvArtifactManager:
    """
    base interface with must implement methods. (no default behaviour)

    note:
        - leverage environment variables for configurability
        - avoid writing in to memory to avoid any pass-forward inter-dependencies
        - use to leverage your ml tools i.e. dvc, mlflow, wandb, etc
    """

    def __init__(self):

        self.custom_environment = base.BaseEnvironment()

    @staticmethod
    def download_assets(fs_base_path, local_path, storage_location):
        raise NotImplementedError("Must implement a download assets functionality")

    @staticmethod
    def upload_assets(fs_base_path, local_path, storage_location):
        raise NotImplementedError("Must implement a upload assets functionality")


    def setup_inputs(self):
        """Iterates and downloads assets remoate -> input channels"""
        logger.debug(
            (
                "Setup assets in {INPUT_DATA_DIR}".format(
                    INPUT_DATA_DIR=self.custom_environment.input_data_dir
                )
            )
        )
        # only fetch channels of environment prefix MLDOCK_INPUT_CHANNEL_
        channels = self.custom_environment.get_input_channel_iter()

        if len(channels) == 0:
            logger.debug("No input channels were found in ENV VARS.")

        for channel in channels:
            channel_path = channel["key"].replace("MLDOCK_INPUT_CHANNEL_", "").lower()
            local_channel_path = Path(self.custom_environment.input_data_dir, channel_path)
            try:
                path_without_scheme = utils.strip_scheme(channel["value"])

                self.download_assets(
                    fs_base_path=path_without_scheme,
                    local_path=local_channel_path,
                    storage_location=".",
                )

            except FileExistsError:
                logger.debug(
                    (
                        "{CHANNEL_KEY} Channel skipped. Already exists".format(
                            CHANNEL_KEY=channel["key"]
                        )
                    )
                )

    def cleanup_outputs(self):
        """Iterates and uploads output channel -> remote"""
        logger.debug("Cleanup assets in {}".format(self.custom_environment.output_data_dir))
        # only fetch channels of environment prefix MLDOCK_OUTPUT_CHANNEL_
        channels = self.custom_environment.get_output_channel_iter()

        if len(channels) == 0:
            logger.debug("No output channels were found in ENV VARS.")

        for channel in channels:
            # only fetch channels with output
            channel_path = channel["key"].replace("MLDOCK_OUTPUT_CHANNEL_", "").lower()
            local_channel_path = Path(self.custom_environment.output_data_dir, channel_path)
            try:
                path_without_scheme = utils.strip_scheme(channel["value"])

                self.upload_assets(
                    fs_base_path=path_without_scheme,
                    local_path=local_channel_path,
                    storage_location=".",
                    zip_artifacts=True,
                )

            except AssertionError:
                logger.debug(
                    "Skipping channel. {LOCAL_CHANNEL_PATH} is not a "
                    "directory or could not be found".format(
                        LOCAL_CHANNEL_PATH=local_channel_path
                    )
                )

    def setup_model_artifacts(self):
        """Iterates and downloads assets remoate -> model channel"""
        logger.debug("Setup model assets in {}".format(self.custom_environment.model_dir))
        # only fetch channels of environment prefix MLDOCK_MODEL_INPUT_CHANNEL_
        channels = self.custom_environment.get_model_input_channel_iter()

        if len(channels) == 0:
            logger.debug("No input channels were found in ENV VARS.")

        for channel in channels:
            channel_path = (
                channel["key"].replace("MLDOCK_MODEL_INPUT_CHANNEL_", "").lower()
            )
            local_channel_path = Path(self.custom_environment.model_dir, channel_path)
            try:
                path_without_scheme = utils.strip_scheme(channel["value"])
                self.download_assets(
                    fs_base_path=path_without_scheme,
                    local_path=local_channel_path,
                    storage_location=".",
                )

            except FileExistsError:
                logger.debug(
                    (
                        "{CHANNEL_KEY} Channel skipped. Already exists".format(
                            CHANNEL_KEY=channel["key"]
                        )
                    )
                )

    def cleanup_model_artifacts(self):
        """Iterates and uploads from model channel -> remote"""
        logger.debug("Cleanup model assets in {}".format(self.custom_environment.model_dir))

        # only fetch channels of environment prefix MLDOCK_MODEL_OUTPUT_CHANNEL_
        channels = self.custom_environment.get_model_output_channel_iter()

        if len(channels) == 0:
            logger.debug("No model channels were found in ENV VARS.")

        for channel in channels:
            channel_path = (
                channel["key"].replace("MLDOCK_MODEL_OUTPUT_CHANNEL_", "").lower()
            )
            local_channel_path = Path(self.custom_environment.model_dir, channel_path)

            try:

                path_without_scheme = utils.strip_scheme(channel["value"])
                
                self.upload_assets(
                    fs_base_path=path_without_scheme,
                    local_path=local_channel_path,
                    storage_location=".",
                    zip_artifacts=True,
                )

            except AssertionError:
                logger.debug(
                    "Skipping channel. {LOCAL_CHANNEL_PATH} is not a "
                    "directory or could not be found".format(
                        LOCAL_CHANNEL_PATH=local_channel_path
                    )
                )
