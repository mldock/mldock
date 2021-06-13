"""
    TRAINER SCRIPT - contains custom code for training your model
"""
import os
import sys
import json
import argparse
import logging

# Add sagemaker environment in training
from src.container.assets import environment, logger

def str2bool(arg_value: str) -> bool:
    if isinstance(arg_value, bool):
        return arg_value
    if arg_value.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif arg_value.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')

def str2dict(arg_value: str) -> dict:
    d_argvalue = json.loads(arg_value)
    if isinstance(d_argvalue, dict):
        return d_argvalue
    else:
        raise argparse.ArgumentTypeError('Json Dictionary expected.')

def run_training():
    PARSER= argparse.ArgumentParser()
    ## User set params which link to Sagemaker params
    PARSER.add_argument('--iris', type=str,
                        default=environment.channel_input_dirs["iris"],
                        help='Path to data')
    PARSER.add_argument('--factors', default=environment.hyperparameters.get('factors', 20),
                        type=int,
                        help='Number of factorization factors to compute during model fit.')
    PARSER.add_argument('--regularization', default=environment.hyperparameters.get('regularization', 0.3),
                        type=int,
                        help='Coefficient of regularization to apply during model fit.')
    PARSER.add_argument('--iterations', default=environment.hyperparameters.get('iterations', 10),
                        type=int,
                        help='Number iterations of the dataset should be run during model fit.')
    PARSER.add_argument('--run_eval', default=environment.hyperparameters.get('run_eval', True),
                        type=str2bool,
                        help='Whether to run metrics evaluation prior to training model on full data.')
    PARSER.add_argument('--refit', default=environment.hyperparameters.get('refit', True),
                        type=str2bool,
                        help='Whether or not to save model.')

    # Get args
    ARGS, _ = PARSER.parse_known_args()

    if ARGS.run_eval:
        logger.info('Running Evaluation')
        # TODO Add your Evaluation Fitting here
        
        logger.info("Your data is here = {}".format(ARGS.iris))

        logger.info("Some hyperparameters = factors={}, regularization={}, iterations={}".format(ARGS.factors, ARGS.regularization, ARGS.iterations))


    # save model to s3
    if ARGS.refit:
        logger.info('Refitting Final Model')
        # TODO Add model.fit(X) here again


        # save model to s3
        logger.info("Model saved in {}. This is written back to s3 at job completion.".format(environment.model_dir))
        model_dir = os.path.join(environment.model_dir,'model.pkl')
        # TODO add model saving workflow here
        pass
    else:
        logger.info("Skipping model save step. ")
