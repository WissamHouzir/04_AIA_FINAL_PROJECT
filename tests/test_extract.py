# tests/test_extract.py
import os
import json
from dags.climate_news_api_dag import _extract_data
from tests.conftest import FakeTI
import pytest
import requests

def test_extract_data_success(mocker, tmp_path):
    # Mock API
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = [
        {"Text": "news 1", "Label": "fake"}
    ]
    mocker.patch("requests.get", return_value=mock_response)

    # Mock dossier data
    mocker.patch("builtins.open", mocker.mock_open())
    mocker.patch("json.dump")

    ti = FakeTI()
    _extract_data(ti)

    assert "filename" in ti.store
