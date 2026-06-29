# tests/test_transform.py
import json
import pandas as pd
from dags.climate_news_api_dag import _transform_data
from tests.conftest import FakeTI
import pytest
import requests

def test_transform_data(mocker, tmp_path):
    # Fake input file
    input_file = tmp_path / "input.json"
    json.dump(
        [{"Text": "some climate news", "Label": "true"}],
        open(input_file, "w")
    )

    # Fake TI
    ti = FakeTI()
    ti.xcom_push("filename", str(input_file))

    # Mock predict API
    mock_post = mocker.Mock()
    mock_post.json.return_value = {"prediction": [2]}
    mock_post.raise_for_status.return_value = None
    mocker.patch("requests.post", return_value=mock_post)

    _transform_data(ti)

    output_file = ti.store["filename"]
    df = pd.read_csv(output_file)

    assert "pred_label" in df.columns
    assert df["is_true"].iloc[0] == 1
