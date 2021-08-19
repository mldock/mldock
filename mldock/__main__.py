"""MLDOCK CLI MAIN ENTRYPOINT SCIPT"""
# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals

import os
import click

from mldock.__version__ import __version__
from mldock.__init__ import MLDOCK_LOGO
from mldock.command.container import container
from mldock.command.configure import configure
from mldock.command.local import local
from mldock.command.registry import registry
from mldock.command.templates import templates
from mldock.command.logs import logs
from mldock.command.packages import packages
from mldock.log import configure_logger

click.disable_unicode_literals_warning = True

CLI_VERSION = 'Version: cli {}'.format(__version__)

@click.group()
@click.version_option(message='{}\n{}'.format(MLDOCK_LOGO, CLI_VERSION))
@click.option(u"-v", u"--verbose", count=True, help=u"Turn on debug logging")
@click.pass_context
def cli(ctx, verbose):
    """
    A CLI that helps put machine learning in places that empower ml developers
    """
    mldock_package_path = os.path.dirname(os.path.realpath(__file__))
    logger=configure_logger('mldock', verbose=verbose)
    logger.info(MLDOCK_LOGO)
    logger.info(CLI_VERSION)
    ctx.obj = {'verbose': verbose, 'mldock_package_path': mldock_package_path, 'logo': MLDOCK_LOGO}

def add_commands(cli_group: click.group):
    """
        add commands to cli group
        args:
            cli (click.group)
    """
    cli_group.add_command(configure)
    cli_group.add_command(container)
    cli_group.add_command(local)
    cli_group.add_command(registry)
    cli_group.add_command(templates)
    cli_group.add_command(logs)
    cli_group.add_command(packages)

add_commands(cli)

if __name__ == '__main__':
    # pylint: disable=no-value-for-parameter
    cli()
