"""Container API methods"""
import os
import json
import logging
from pathlib import Path
from future.moves import subprocess

from mldock.config_managers.container import MLDockConfigManager
from mldock.platform_helpers import utils

logger=logging.getLogger('mldock')

def init_container_project(dir, mldock_package_path, mldock_config, testing_framework, service, container_only, template_dir):

    logger.info("Initializing Container Project")
    src_directory = os.path.join(
        dir,
        mldock_config.get("mldock_module_dir", "src")
    )
    service_directory = os.path.join(
        dir,
        'service'
    )

    logger.info("getting template")

    if template_dir is None:
        template_dir = os.path.join(
            mldock_package_path,
            "templates",
            mldock_config['platform']
        )
        logger.debug("--- no template dir provided, using = (Default) {}".format(mldock_config['platform']))

    logger.debug("Template directory = {}".format(template_dir))


    mldock_module_path = os.path.join(
        src_directory,
        'container'
    )

    test_path = os.path.join(mldock_module_path, 'local_test', 'test_dir')

    logger.info("Setting up workspace")   
    logger.debug("Adding container")
    utils._copy_boilerplate_to_dst(
        os.path.join(template_dir, 'src/container'),
        mldock_module_path,
        remove_first=True
    )
    if container_only == False:
        logger.debug("Adding src scripts")
        utils._copy_boilerplate_to_dst(os.path.join(template_dir, 'src/'), src_directory)

    if testing_framework == 'pytest':
        logger.info("Adding pytest container tests")
        utils._copy_boilerplate_to_dst(os.path.join(template_dir, 'tests/'), 'tests/')
        logger.debug("renaming test file")

        utils._rename_file(
            base_path='tests/container_health',
            current_filename='_template_test_container.py',
            new_filename='test_{ASSET_DIR}.py'.format(ASSET_DIR=dir)
        )
    if service is not None:
        logger.info("Adding {} service".format(service))
        utils._copy_boilerplate_to_dst(os.path.join(template_dir, 'service', service), service_directory)

    logger.info("Adding some extra goodies")
    utils._write_json({}, Path(dir,'config/hyperparameters.json'))
