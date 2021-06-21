from __future__ import print_function, absolute_import
import sys;sys.path.insert(1, ".")  # Do not remove this
import subprocess
import sys

import os
import json
import sys
import traceback
from src.trainer import run_training
from src.container.assets import TrainingContainer, environment, logger

def train_function():
    """
    The function to execute the training.

    :param input_data_path: [str], input directory path where all the training file(s) reside in
    :param model_save_path: [str], directory path to save your model(s)
    :param hyperparams_path: [optional[str], default=None], input path to hyperparams json file.

    """

    logger.info('Starting the training.')
    try:

        # custom recommender training code
        run_training()

        logger.info('Training complete.')
    except Exception as e:
        # Write out an error file. This will be returned as the failureReason in the
        # DescribeTrainingJob result.
        trc = traceback.format_exc()
        with open(os.path.join('/opt/ml/output/failure'), 'w') as s:
            s.write('Exception during training: ' + str(e) + '\n' + trc)
        # Printing this causes the exception to be in the training job logs, as well.
        logger.error('Exception during training: ' + str(e) + '\n' + trc)
        raise

if __name__ == '__main__':

    training = TrainingContainer(environment=environment)
    try:
        training.startup()

        train_function()
    except Exception as exception:
        logger.error(exception)
    finally:
        training.cleanup()

    # A zero exit code causes the job to be marked a Succeeded.
    sys.exit(0)
