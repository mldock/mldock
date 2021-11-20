"""Test Predict API calls"""
import io
from PIL import Image
from dataclasses import dataclass
import tempfile
from pathlib import Path
import pytest
from mock import patch
from mldock.api.predict import send_image_jpeg, send_csv, send_json, handle_prediction
import responses
import requests


@pytest.fixture
def image_bytes():
    """reads image as bytes string"""

    img = Image.open("tests/api/fixtures/eight.png", mode="r")
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format="PNG")
    return img_byte_arr.getvalue()


@dataclass
class MockResponse:

    status_code: int
    json_data: dict = None
    text: str = None
    _content: bytes = None

    def json(self):
        return self.json_data


class TestPredictAPI:

    """
    TEST ERROR STATUS_CODE!=200 SCENERIO
    """

    @staticmethod
    @responses.activate
    def test_handle_prediction_send_json_handles_non_200():

        responses.add(
            responses.POST,
            "http://nothing-to-see-here/invocations",
            json={"error": "client error"},
            status=404,
        )
        with pytest.raises(requests.exceptions.RequestException):
            _ = handle_prediction(
                host="http://nothing-to-see-here/invocations",
                request="tests/api/fixtures/payload.json",
                response_file=None,
                request_content_type="application/json",
                response_content_type="application/json",
            )

    @staticmethod
    @responses.activate
    def test_handle_prediction_sending_image_jpeg_handles_non_200():

        responses.add(
            responses.POST,
            "http://nothing-to-see-here/invocations",
            json={"error": "client error"},
            status=404,
        )
        with pytest.raises(requests.exceptions.RequestException):
            _ = handle_prediction(
                host="http://nothing-to-see-here/invocations",
                request="tests/api/fixtures/eight.png",
                response_file=None,
                request_content_type="image/jpeg",
                response_content_type="application/json",
            )

    @staticmethod
    @responses.activate
    def test_handle_prediction_sending_text_csv_handles_non_200():

        responses.add(
            responses.POST,
            "http://nothing-to-see-here/invocations",
            json={"error": "client error"},
            status=404,
        )
        with pytest.raises(requests.exceptions.RequestException):
            _ = handle_prediction(
                host="http://nothing-to-see-here/invocations",
                request="tests/api/fixtures/payload.csv",
                response_file=None,
                request_content_type="text/csv",
                response_content_type="application/json",
            )

    """
        TEST SUCCESS STATUS_CODE=200 SCENERIO
    """

    @staticmethod
    def test_handle_prediction_send_json_success_200():

        with patch("mldock.api.predict.execute_request") as mock_execute_request:
            mock_execute_request.return_value = MockResponse(
                json_data={"result": "success"}, status_code=200
            )
            _ = handle_prediction(
                host="http://nothing-to-see-here/invocations",
                request="tests/api/fixtures/payload.json",
                response_file=None,
                request_content_type="application/json",
                response_content_type="application/json",
            )

            validation_kwargs = {
                "url": "http://nothing-to-see-here/invocations",
                "headers": {"Content-Type": "application/json"},
            }
            _, kwargs = list(mock_execute_request.call_args)

            data_obj = kwargs.pop("data")
            assert (
                kwargs == validation_kwargs
            ), "Failure. URL and Headers are incorrect."
            assert isinstance(data_obj, str), "Failure. Expected str json object."

    @staticmethod
    def test_handle_prediction_sending_image_jpeg_success_200(image_bytes):

        with patch("mldock.api.predict.execute_request") as mock_execute_request:
            mock_execute_request.return_value = MockResponse(
                _content=image_bytes, status_code=200
            )
            _ = handle_prediction(
                host="http://nothing-to-see-here/invocations",
                request="tests/api/fixtures/eight.png",
                response_file=None,
                request_content_type="image/jpeg",
                response_content_type="image/jpeg",
            )
            validation_kwargs = {
                "url": "http://nothing-to-see-here/invocations",
                "headers": {"Content-Type": "image/jpeg"},
            }
            _, kwargs = list(mock_execute_request.call_args)

            data_obj = kwargs.pop("data")
            assert (
                kwargs == validation_kwargs
            ), "Failure. URL and Headers are incorrect."
            assert isinstance(
                data_obj, io.BytesIO
            ), "Failure. Expected io.BytesIO object."

    @staticmethod
    def test_handle_prediction_sending_text_csv_success_200():

        with patch("mldock.api.predict.execute_request") as mock_execute_request:
            mock_execute_request.return_value = MockResponse(
                text="greet,name\nhello,sam", status_code=200
            )
            _ = handle_prediction(
                host="http://nothing-to-see-here/invocations",
                request="tests/api/fixtures/payload.csv",
                response_file=None,
                request_content_type="text/csv",
                response_content_type="text/csv",
            )

            validation_kwargs = {
                "url": "http://nothing-to-see-here/invocations",
                "headers": {"Content-Type": "text/csv"},
            }
            _, kwargs = list(mock_execute_request.call_args)

            data_obj = kwargs.pop("data")
            assert (
                kwargs == validation_kwargs
            ), "Failure. URL and Headers are incorrect."
            assert isinstance(data_obj, str), "Failure. Expected str json object."

    """
        TEST WRITING RESPONSE TO FILE SCENERIO
    """

    @staticmethod
    def test_handle_prediction_send_json_success_write_response_file():

        with tempfile.TemporaryDirectory() as tmp_dir:

            response_filepath = Path(tmp_dir, "response.json")
            with patch("mldock.api.predict.execute_request") as mock_execute_request:
                mock_execute_request.return_value = MockResponse(
                    json_data={"result": "success"}, status_code=200
                )
                _ = handle_prediction(
                    host="http://nothing-to-see-here/invocations",
                    request="tests/api/fixtures/payload.json",
                    response_file=response_filepath,
                    request_content_type="application/json",
                    response_content_type="application/json",
                )

                assert (
                    response_filepath.is_file()
                ), "Failure. outputfile was not created"

    @staticmethod
    def test_handle_prediction_sending_image_jpeg_success_write_response_file(
        image_bytes,
    ):

        with tempfile.TemporaryDirectory() as tmp_dir:

            response_filepath = Path(tmp_dir, "response.png")
            with patch("mldock.api.predict.execute_request") as mock_execute_request:
                mock_execute_request.return_value = MockResponse(
                    _content=image_bytes, status_code=200
                )
                _ = handle_prediction(
                    host="http://nothing-to-see-here/invocations",
                    request="tests/api/fixtures/eight.png",
                    response_file=response_filepath,
                    request_content_type="image/jpeg",
                    response_content_type="image/jpeg",
                )
                assert (
                    response_filepath.is_file()
                ), "Failure. outputfile was not created"

    @staticmethod
    def test_handle_prediction_sending_text_csv_success_write_response_file():

        with tempfile.TemporaryDirectory() as tmp_dir:

            response_filepath = Path(tmp_dir, "response.csv")
            with patch("mldock.api.predict.execute_request") as mock_execute_request:
                mock_execute_request.return_value = MockResponse(
                    text="greet,name\nhello,sam", status_code=200
                )
                _ = handle_prediction(
                    host="http://nothing-to-see-here/invocations",
                    request="tests/api/fixtures/payload.csv",
                    response_file=response_filepath,
                    request_content_type="text/csv",
                    response_content_type="text/csv",
                )

                assert (
                    response_filepath.is_file()
                ), "Failure. outputfile was not created"

    """
        TEST ADDING ADDTIONAL HEADERS
    """

    @staticmethod
    def test_handle_prediction_send_json_success_add_headers():

        with patch("mldock.api.predict.execute_request") as mock_execute_request:
            mock_execute_request.return_value = MockResponse(
                json_data={"result": "success"}, status_code=200
            )
            _ = handle_prediction(
                host="http://nothing-to-see-here/invocations",
                request="tests/api/fixtures/payload.json",
                response_file=None,
                request_content_type="application/json",
                response_content_type="application/json",
                headers={"Authentication": "bearer 12345"},
            )

            validation_kwargs = {
                "url": "http://nothing-to-see-here/invocations",
                "headers": {
                    "Content-Type": "application/json",
                    "Authentication": "bearer 12345",
                },
            }
            _, kwargs = list(mock_execute_request.call_args)

            kwargs.pop("data")
            assert (
                kwargs == validation_kwargs
            ), "Failure. URL and Headers are incorrect."
