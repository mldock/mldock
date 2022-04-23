"""
    TRAINER SCRIPT - contains custom code for training your model
"""
import os
import argparse
import pickle

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

from src.container.lifecycle import training_container

@training_container.wrap
def run_training(environment, logger):
    """Run training worflow"""
    parser = argparse.ArgumentParser()
    # get parameters
    parser.add_argument(
        "--iris",
        type=str,
        default=os.path.join(environment.input_data_dir, "iris"),
        help="Expects a .csv file, representing the lookup.",
    )
    parser.add_argument(
        "--test_size",
        type=float,
        default=environment.hyperparameters.get("test_size", 0.33),
        help="size of test sample to evaluate on.",
    )
    # Get args
    args, _ = parser.parse_known_args()

    data = pd.read_csv(os.path.join(args.iris, "train.csv"))
    X, y = data.drop(["target"], axis=1), data["target"]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=args.test_size, random_state=123, shuffle=True
    )

    transformer = StandardScaler()
    transformer.fit(X_train)
    X_train_std = transformer.transform(X_train)
    X_test_std = transformer.transform(X_test)

    logger.info("Running Training")

    model = SVC(kernel="rbf", random_state=0, gamma=0.10, C=1.0)
    model.fit(X_train_std, y_train)

    logger.info("Running Evaluation")
    logger.info(f"train_accuracy={model.score(X_train_std, y_train)};")
    logger.info(f"test_accuracy={model.score(X_test_std, y_test)};")

    logger.info("Save Model artifacts")
    transformer_path = os.path.join(environment.model_dir, "iris/transformer.pkl")

    with open(transformer_path, "wb") as file_:
        pickle.dump(transformer, file_)

    model_path = os.path.join(environment.model_dir, "iris/model.pkl")

    with open(model_path, "wb") as file_:
        pickle.dump(model, file_)
