import os
import io
import csv
import logging
import numpy as np
from mldock.platform_helpers.mldock.errors import extract_stack_trace
from mldock.platform_helpers.mldock.model_service import base
from src.container.assets import environment, logger

class ModelService(base.ModelService):
    model = None

    def load_model(self, model_path):
        """Get the model object for this instance, loading it if it's not already loaded."""
        if self.model == None:
            # TODO place your model load code here
            # get your model from MODEL_DIR
            self.model = None
        return self.model

    @staticmethod
    def input_transform(input):
        """
            Custom input transformer

            args:
                input: raw input from request
        """
        return input

    @staticmethod
    def output_transform(predictions):
        """
            Custom output transformation code
        """
        return predictions

    def predict(self, input):
        """For the input, do the predictions and return them.

        Args:
            input (a pandas dataframe): The data on which to do the predictions. There will be
                one prediction per row in the dataframe"""
        try:
            logger.info("Model = {}".format(self.model))
            # TODO replace this with your model.predict
            pred = np.array(['pred_1', 'pred_2', 'pred_3'])
            logger.info(pred)
            return pred
        except Exception as exception:
            # get stack trace as exception
            stack_trace = extract_stack_trace()
            reformatted_log_msg = (
                    'Server Error: {ex}'.format(ex=stack_trace)
            )
            return reformatted_log_msg


def handler(json_input):
    """
    Prediction given the request input
    :param json_input: [dict], request input
    :return: [dict], prediction
    """
    
    model_service = ModelService(model_path=os.path.join(environment.model_dir, "model.joblib"))

    # TODO input transformer
    model_input = model_service.input_transform(input)

    # TODO model prediction
    pred = model_service.predict(model_input)
    logger.info(pred)
    # TODO Add any output processing
    results = model_service.output_transform(
        predictions=pred
    )

    return results
