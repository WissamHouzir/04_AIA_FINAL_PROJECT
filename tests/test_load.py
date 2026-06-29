# tests/test_load.py
import pandas as pd
from dags.climate_news_api_dag import _load_data
from tests.conftest import FakeTI
import pytest
import requests

def test_load_data(mocker, tmp_path):
    csv_file = tmp_path / "data.csv"
    pd.DataFrame({"a": [1]}).to_csv(csv_file, index=False)

    ti = FakeTI()
    ti.xcom_push("filename", str(csv_file))

    mock_engine = mocker.Mock()
    mocker.patch("sqlalchemy.create_engine", return_value=mock_engine)
    mocker.patch("pandas.DataFrame.to_sql")

    _load_data(ti)
