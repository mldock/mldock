"""
    TRAINER SCRIPT - contains custom code for training your model
"""
import os
import sys
import json
import argparse
import pickle
from src.container.assets import environment, logger
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import cross_val_score
from sklearn.svm import SVC

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
                        default=os.path.join(environment.input_data_dir, 'iris'),
                        help='Expects a .csv file, representing the lookup.')
    PARSER.add_argument('--test-size', default=environment.hyperparameters.get('test-size', 0.2),
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

    logger.info("Experiment id = {}".format(environment.environment_variables('MLDOCK_EXPERIMENT_ID', default=None)))

    data = pd.read_csv(os.path.join(ARGS.iris, 'train.csv'))
    X, y = data.drop(['target'], axis=1), data['target']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=ARGS.test_size, random_state=123, shuffle=True)

    transformer = StandardScaler()
    transformer.fit(X_train)
    X_train_std = transformer.transform(X_train)
    X_test_std = transformer.transform(X_test)

    if ARGS.run_eval:
        logger.info('Running Evaluation')

        model = SVC(kernel='rbf', random_state=0, gamma=.10, C=1.0)
        model.fit(X_train_std, y_train)

        print('Model: Accuracy (train) {:.2f}'.format(model.score(X_train_std, y_train)))
        print('Model: Accuracy (test) {:.2f}'.format(model.score(X_test_std, y_test)))

    if ARGS.refit:
        logger.info('Refitting Final Model')

        transformer = StandardScaler()
        transformer.fit(X)
        X_std = transformer.transform(X)
        model = SVC(kernel='rbf', random_state=0, gamma=.10, C=1.0)
        model.fit(X_std, y)

        logger.info("Model saved in {}. This is written back to remote at job completion.".format(environment.model_dir))
        transformer_path = os.path.join(environment.model_dir, 'iris/transformer.pkl')

        with open(transformer_path, 'wb') as file_:
            pickle.dump(transformer, file_)

        model_path = os.path.join(environment.model_dir, 'iris/model.pkl')

        with open(model_path, 'wb') as file_:
            pickle.dump(model, file_)
    else:
        logger.debug("Skipping model save step. ")

if __name__ == '__main__':

    try:
        run_training()
    except Exception as exception:
        logger.error(exception)
