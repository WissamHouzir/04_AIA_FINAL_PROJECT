import json
import logging
import os
import requests
from datetime import datetime
import pandas as pd
from sqlalchemy import create_engine
from airflow import DAG
from airflow.models import Variable
from airflow.operators.python import PythonOperator

API_ENDPOINT =Variable.get("API_ENDPOINT", "https://olivier-52-real-time-climate-fake-news.hf.space/get_news")
PREDICT_ENDPOINT = Variable.get("PREDICT_ENDPOINT", "https://olivier-52-climate-fake-news-api.hf.space/predict")

def _extract_data(ti):
    url = API_ENDPOINT
    headers = {'accept': 'application/json'}
    
    try:
        response = requests.get(url=url, headers=headers)
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)

    if response.status_code == 200:
        data = response.json()
        logging.info("API fetch successful")
    else:
        logging.error(f"API call failed with status code:", response.status_code)
    
    now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    with open(f"./data/climate_news_{now}.json", "w") as f:
        json.dump(data, f)
    logging.info(f"Data saved in climate_news_{now}.json")
    ti.xcom_push(key="filename", value=f"./data/climate_news_{now}.json")

def _transform_data(ti):
    file = ti.xcom_pull(task_ids="extract_data", key="filename")
    with open(file, 'r') as f:
        data = json.load(f)
        dataframe = pd.DataFrame(data)
    os.remove(file) #remove tmp json file

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    preds = []
    for row in dataframe['Text']:
        text = row[:500]
        response = requests.post(
                        PREDICT_ENDPOINT,
                        json={"text": text},
                        timeout=30
                    )
        response.raise_for_status()
        preds.append(int(response.json()['prediction'][-1]))

    dataframe['pred_label'] = preds
    dataframe['pred_label'] = dataframe['pred_label'].map({0: 'biased', 1: 'fake', 2: 'true'})
    dataframe['created_at'] = now
    dataframe['is_true'] = dataframe['pred_label'].apply(lambda x: 1 if x == 'true' else 0)
    dataframe['is_fake'] = dataframe['pred_label'].apply(lambda x: 1 if x == 'fake' else 0)
    dataframe['is_biased'] = dataframe['pred_label'].apply(lambda x: 1 if x == 'biased' else 0)
    dataframe.rename(columns={'Text': 'text', 'Label': 'label'}, inplace=True)
    logging.info("Model prediction done")

    dataframe.to_csv(f"./data/climate_news_data_{now}.csv", index=False)
    ti.xcom_push(key="filename", value=f"./data/climate_news_data_{now}.csv")
    logging.info("Data saved in climate_news_data.csv")
    
def _load_data(ti):
    file = ti.xcom_pull(task_ids="transform_data", key="filename")

    dataframe = pd.read_csv(file)
    engine = create_engine('postgresql://airflow:airflow@postgres:5432/airflow')
    dataframe.to_sql('climate_news_data', engine, index=False, if_exists='append')
    
    logging.info("Data loaded in database")
    os.remove(file) #remove tmp csv file
    
with DAG("climate_news_api_dag", start_date=datetime(2026, 2, 5), schedule="* * * * *", catchup=False) as dag:
    extract_data = PythonOperator(task_id="extract_data", python_callable=_extract_data)
    transform_data = PythonOperator(task_id="transform_data", python_callable=_transform_data)
    load_data = PythonOperator(task_id="load_data", python_callable=_load_data)

    extract_data >> transform_data >> load_data