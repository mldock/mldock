"""Training entrypoint script"""
from __future__ import print_function, absolute_import
import sys;sys.path.insert(1, ".")  # Do not remove this
from src.trainer import run_training


if __name__ == '__main__':
    # run training workflow
    run_training()
