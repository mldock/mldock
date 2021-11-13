"""Predict Request API utilties"""
import io
import json
import csv
import requests

def execute_request(url, headers, data):
    """compiles and executes request to API"""
    return requests.post(
        url=url,
        headers=headers,
        data=data
    )

def save_bytes_as_png(bytes_img, filepath):
    """save bytes image as png throgh pillow"""
    image = Image.frombytes('RGB', (512, 512), bytes_img)
    image.save(filepath)

def save_json(json_data, filepath):
    """save json data to .json"""
    with open(filepath, "w") as file_:
        json.dump(json_data, file_)

def save_csv(text_data, filepath):
    """save text data as csv/txt"""
    with open(filepath, "w") as file_:
        writer = csv.writer(f)

        for row in text_data:
            writer.writerow(row)

def send_json(data, host):
    """Send a json payload in request providing a filepath."""

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

    return response

def send_csv(data, host):
    """Send a json payload in request providing a filepath."""

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
    return response

def send_image_jpeg(data, host):
    """Send a image jpeg payload as bytes in request providing a filepath."""

    response = execute_request(
        url=host,
        headers={'Content-Type': 'image/jpeg'},
        data=data
    )

    if response.status_code != 200:
        raise requests.exceptions.RequestException(
            "error ({}): {}".format(
                response.status_code,
                response.raise_for_status()
            )
        )
    return response

def handle_request(host, file_path, content_type):

    if content_type == 'application/json':

        with open(file_path, 'r') as file_:
            data = json.load(file_)

        response_obj = send_json(data, host)
        return response_obj

    elif content_type == 'image/jpeg':

        with open(file_path, 'rb') as file_:
            data = io.BytesIO(file_.read())

        response_obj = send_image_jpeg(data, host)

        return response_obj

    elif content_type == 'text/csv':

        with open(file_path, 'r') as file_:
            data = file_.read()

        response_obj = send_csv(data, host)

        return response_obj


def handle_response(response, content_type, file_path=None):
    """handle response. Extract, transform and emit/write to file"""

    if content_type == 'application/json':

        if file_path is None:
            return response.json()

        elif Path(file_path).is_file():
            save_json(response.json(), file_path)

    elif content_type == 'image/jpeg':

        if file_path is None:
            return response._content

        elif Path(file_path).is_file():
            save_bytes_as_png(response._content, file_path)

    elif content_type == 'text/csv':

        if file_path is None:
            return response.text

        elif Path(file_path).is_file():
            save_csv(response.text, file_path)

def handle_prediction(
    host: str,
    request: str,
    response_file: str = None,
    request_content_type: str = 'application/json',
    response_content_type: str = 'application/json'
):

    # handle request (load to obj, convert, send, get response)
    response_obj = handle_request(
        host=host,
        file_path=request,
        content_type=request_content_type
    )

    # handle reponse (write file, print to terminal)
    return handle_response(
        response=response_obj,
        content_type=response_content_type,
        file_path=response_file
    )
