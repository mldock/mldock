"""
    CONTINAER LIFECYCLE MANAGEMENT

    Provides a central place to instantiate container environment, loggers and container assets management objects.
    Call these instantiated objects in to other scripts using a simple import.
"""
import logging
from mldock.platform_helpers.mldock.configuration.environment.gcp import GCPEnvironment

from src.assets import TrainingContainer, ServingContainer

# Init Environment
environment = GCPEnvironment()

# Set debug level
if environment.environment_variables("MLDOCK_LOGS_LEVEL", None) == "debug":
    log_emit_level = logging.DEBUG
else:
    log_emit_level = logging.INFO

logging.basicConfig(level=log_emit_level)
logger = logging.getLogger("mldock")

# init Training Container
training_container = TrainingContainer(
    container_environment=environment, container_logger=logger
)

# init Serving Container
serving_container = ServingContainer(
    container_environment=environment, container_logger=logger
)
