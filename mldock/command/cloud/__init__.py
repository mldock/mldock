import os
import sys
import logging
import click

from mldock.command.cloud.sagemaker import sagemaker
from mldock.command.cloud.vertex_ai import vertex_ai
from mldock.config_managers.container import \
    MLDockConfigManager
from mldock.terminal import ProgressLogger

click.disable_unicode_literals_warning = True
logger = logging.getLogger('mldock')
MLDOCK_CONFIG_NAME = 'mldock.json'

@click.group()
def cloud():
    """
    Commands to run smoketests in the cloud.
    """
    pass

cloud.add_command(sagemaker)
cloud.add_command(vertex_ai)
