"""
    Serving Endpoint
    This is the file that implements a flask server to do inferences. It's the file that you will
    modify to implement the scoring for your own algorithm.
"""
import os
import numpy as np
from fastapi import FastAPI, Request, HTTPException
import src.prediction as model_serving
from mldock.platform_helpers.mldock.inference.content_encoders import \
    numpy as content_encoders
from mldock.platform_helpers.mldock.model_service.decorators import predictor
from src.container.assets import environment, logger, ServingContainer

app = FastAPI()

# serving workflow utilties
@predictor(container=ServingContainer, environment=environment, logger=logger)
def handler(json_input):
    """
    Handles a request from to the server app
    :param json_input: [dict], request input
    :return: [dict], prediction
    """
    # TODO input transformer
    del json_input

    # TODO model prediction
    pred = np.array(['pred_1', 'pred_2', 'pred_3'])
    logger.info(pred)
    # TODO Add any output processing
    results = pred

    return results

# Serving Endpoints
@app.get('/ping')
async def ping():
    """Determine if the container is working and healthy"""
    return {'message': 'ping!pong!'}


@app.post('/invocations')
async def transformation(request: Request):
    """Do an inference on a single batch of data. In this sample server, we take data as JSON"""
    if request.headers['content-type'] == 'application/json':
        data = request.body
        print(data)

        results = model_serving.handler(
            np.array(data)
        )
        return content_encoders.array_to_json(results)
    else:
        raise HTTPException(
            status_code=415,
            detail={'message': 'This predictor only supports JSON or CSV data'}
        )
