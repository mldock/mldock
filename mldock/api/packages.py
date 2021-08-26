"""Package utilities for managing dependencies with wheel"""

from __future__ import print_function
from __future__ import unicode_literals

import subprocess


def spawn(args, capture_output=False):
    """Spawn a subprocess to execute command"""
    print('=>', ' '.join(args))
    if capture_output:
        return subprocess.check_output(args)
    return subprocess.check_call(args)

def build_wheels(dist_dir, pip_wheel_args):
    """build wheels using pip wheel command line tool"""
    args = [
        'pip', 'wheel',
        '--wheel-dir', dist_dir
    ] + pip_wheel_args
    spawn(args)
    return dist_dir
