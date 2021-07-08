"""Test Predict API calls"""
import io
from dataclasses import dataclass
import pytest
from mock import patch
from mldock.api.predict import send_image_jpeg, send_csv, send_json
import responses
import requests

@pytest.fixture
def image_bytes():
    """reads image as bytes string"""
    with open('tests/api/fixtures/eight.png', 'rb') as file_:
        return io.BytesIO(file_.read())

@dataclass
class MockResponse:

    status_code: int
    json_data: dict = None
    text_data: str = None

    def json(self):
        return self.json_data
    
    def text(self):
        return self.text_data

class TestPredictAPI:

    @staticmethod
    @responses.activate
    def test_send_json_handles_non_200():

        responses.add(
            responses.POST, 'http://nothing-to-see-here/invocations',
            json={'result': 'hello'},
            status=404
        )
        with pytest.raises(requests.exceptions.RequestException):
            _ = send_json(
                filepath="tests/api/fixtures/payload.json",
                host="http://nothing-to-see-here/invocations"
            )

    @staticmethod
    def test_send_image_jpeg_request_gets_correct_input(image_bytes):


        with patch('mldock.api.predict.execute_request') as mock_execute_request:
            mock_execute_request.return_value = MockResponse(json_data={"result": "hello"}, status_code=200)
            result = send_image_jpeg(
                filepath="tests/api/fixtures/eight.png",
                host="http://nothing-to-see-here/invocations"
            )
        
        validation_kwargs = {
            'url': 'http://nothing-to-see-here/invocations',
            'headers': {'Content-Type': 'image/jpeg'}
        }
        _, kwargs = list(mock_execute_request.call_args)

        data_obj = kwargs.pop('data')
        assert kwargs == validation_kwargs, "Failure. URL and Headers are incorrect."
        assert isinstance(data_obj, io.BytesIO), "Failure. Expected io.BytesIO object."

    @staticmethod
    def test_send_json_request_gets_correct_input(image_bytes):


        with patch('mldock.api.predict.execute_request') as mock_execute_request:
            mock_execute_request.return_value = MockResponse(json_data={"result": "hello"}, status_code=200)
            result = send_json(
                filepath="tests/api/fixtures/payload.json",
                host="http://nothing-to-see-here/invocations"
            )
        
        validation_kwargs = {
            'url': 'http://nothing-to-see-here/invocations',
            'headers': {'Content-Type': 'application/json'}
        }
        _, kwargs = list(mock_execute_request.call_args)

        data_obj = kwargs.pop('data')
        assert kwargs == validation_kwargs, "Failure. URL and Headers are incorrect."
        assert isinstance(data_obj, str), "Failure. Expected str json object."

    @staticmethod
    def test_send_csv_request_gets_correct_input(image_bytes):


        with patch('mldock.api.predict.execute_request') as mock_execute_request:
            mock_execute_request.return_value = MockResponse(text_data='result\nhello\n', status_code=200)
            result = send_csv(
                filepath="tests/api/fixtures/payload.csv",
                host="http://nothing-to-see-here/invocations"
            )
        
        validation_kwargs = {
            'url': 'http://nothing-to-see-here/invocations',
            'headers': {'Content-Type': 'text/csv'}
        }
        _, kwargs = list(mock_execute_request.call_args)

        data_obj = kwargs.pop('data')
        assert kwargs == validation_kwargs, "Failure. URL and Headers are incorrect."
        assert isinstance(data_obj, str), "Failure. Expected str json object."
