"""
    Serving Endpoint
    This is the file that implements a flask server to do inferences. It's the file that you will
    modify to implement the scoring for your own algorithm.
"""
import json
import flask
import src.prediction as model_serving
from mldock.platform_helpers.mldock.inference.content_decoders import \
    numpy as content_decoders
from mldock.platform_helpers.mldock.inference.content_encoders import \
    numpy as content_encoders

app = flask.Flask(__name__)

@app.route('/ping', methods=['GET'])
def ping():
    """Determine if the container is working and healthy"""
    return flask.Response(response='\n', status=200, mimetype='application/json')


@app.route('/invocations', methods=['POST'])
def transformation():
    """Do an inference on a single batch of data. In this sample server, we take data as JSON"""
    if flask.request.content_type == 'application/json':
        data = flask.request.get_json()

        results = model_serving.handler(
            content_decoders.decode(json.dumps(data).encode(), content_type='application/json')
        )
        return flask.Response(
            response=content_encoders.encode(
                array_like=results,
                content_type="application/json"
            ),
            status=200,
            mimetype='application/json'
        )
    elif flask.request.content_type == 'text/csv':
        data = flask.request.data

        results = model_serving.handler(
            content_decoders.decode(data, content_type='text/csv'),
        )

        return flask.Response(
            response=content_encoders.encode(
                array_like=results,
                content_type='text/csv'
            ),
            status=200,
            mimetype='text/csv'
        )
    else:
        return flask.Response(
            response=json.dumps({'message': 'This predictor only supports JSON or CSV data'}),
            status=415,
            mimetype='application/json'
        )
