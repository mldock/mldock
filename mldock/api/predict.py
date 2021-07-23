"""Predict Request API utilties"""
import io
import json
import requests

def execute_request(url, headers, data):
    """compiles and executes request to API"""
    return requests.post(
        url=url,
        headers=headers,
        data=data
    )

def send_json(filepath, host):
    """Send a json payload in request providing a filepath."""
    with open(filepath, 'r') as file_:
        data = json.load(file_)

    response = execute_request(
        url=host,
        headers={'Content-Type': 'application/json'},
        data=json.dumps(data)
    )
    if response.status_code != 200:
        raise requests.exceptions.RequestException(
            "error ({}): {}".format(
                response.status_code,
                response.raise_for_status()
            )
        )

    return "{}".format(
        json.dumps(
            response.json(),
            indent=4,
            separators=(',', ': '),
            sort_keys=True
        )
    )

def send_csv(filepath, host):
    """Send a json payload in request providing a filepath."""
    with open(filepath, 'r') as file_:
        data = file_.read()

    response = execute_request(
        url=host,
        headers={'Content-Type': 'text/csv'},
        data=data
    )

    if response.status_code != 200:
        raise requests.exceptions.RequestException(
            "error ({}): {}".format(
                response.status_code,
                response.raise_for_status()
            )
        )
    return response.text

def send_image_jpeg(filepath, host):
    """Send a image jpeg payload as bytes in request providing a filepath."""

    with open(filepath, 'rb') as file_:
        byte_content = io.BytesIO(file_.read())

    response = execute_request(
        url=host,
        headers={'Content-Type': 'image/jpeg'},
        data=byte_content
    )

    if response.status_code != 200:
        raise requests.exceptions.RequestException(
            "error ({}): {}".format(
                response.status_code,
                response.raise_for_status()
            )
        )
    return "{}".format(
        json.dumps(
            response.json(),
            indent=4,
            separators=(',', ': '),
            sort_keys=True
        )
    )
