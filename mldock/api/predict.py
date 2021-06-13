"""Predict Request API utilties"""
import requests
import json

def send_json(filepath, host):
    """Send a json payload in request providing a filepath."""
    with open(filepath, 'r') as file_:
        data = json.load(file_)

    response = requests.post(
        host,
        headers={'Content-Type': 'application/json'},
        data=json.dumps(data)
    )
    if response.status_code == 200:
        return "{}".format(json.dumps(response.json(), indent=4, separators=(',', ': '), sort_keys=True))
    else:
        raise requests.exceptions.RequestException("error ({}): {}".format(response.status_code, response.raise_for_status()))

def send_csv(filepath, host):
    """Send a json payload in request providing a filepath."""
    with open(filepath, 'r') as file_:
        data = file_.read()

        response = requests.post(
            host,
            headers={'content-type': 'text/csv'},
            data=data
        )

    if response.status_code == 200:
        return response.text
    else:
        raise requests.exceptions.RequestException("error ({}): {}".format(response.status_code, response.raise_for_status()))