"""
    Serving Endpoint
    This is the file that implements a flask server to do inferences. It's the file that you will
    modify to implement the scoring for your own algorithm.
"""
import numpy as np
from fastapi import FastAPI, Request, HTTPException
from mldock.platform_helpers.mldock.inference.content_encoders import (
    numpy as content_encoders,
)
from src.container.lifecycle import serving_container

app = FastAPI()

@app.on_event("startup")
def startup_event():
    serving_container.startup()


@app.on_event("shutdown")
def shutdown_event():
    serving_container.cleanup()


# serving workflow utilties
@serving_container.wrap
def handler(json_input, environment, logger, **kwargs):
    """
    Handles a request from to the server app
    :param json_input: [dict], request input
    :return: [dict], prediction
    """
    # TODO input transformer
    del json_input

    # TODO model prediction
    pred = np.array(["pred_1", "pred_2", "pred_3"])
    logger.info(pred)
    # TODO Add any output processing
    results = pred

    return results


# Serving Endpoints
@app.get("/ping")
async def ping():
    """Determine if the container is working and healthy"""
    return {"message": "ping!pong!"}


@app.post("/invocations")
async def transformation(request: Request):
    """Do an inference on a single batch of data. In this sample server, we take data as JSON"""
    if request.headers["content-type"] == "application/json":
        data = await request.body()
        print(data)

        results = handler(np.array(data))
        return content_encoders.array_to_json(results)
    else:
        raise HTTPException(
            status_code=415,
            detail={"message": "This predictor only supports JSON or CSV data"},
        )
