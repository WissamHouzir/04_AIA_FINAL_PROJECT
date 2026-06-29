import pandas as pd
from sqlalchemy import create_engine
from datetime import datetime
from evidently import Dataset
from evidently import DataDefinition
from evidently import Report
from evidently.metrics import *
from evidently import MulticlassClassification
from evidently.presets import DataDriftPreset, ClassificationPreset
from airflow import DAG
from airflow.models import Variable
from airflow.operators.python import PythonOperator

REFERENCE_STORE = Variable.get("REFERENCE_STORE", "./data/reference_data.csv")

def _generate_evidently_report():
    reference = pd.read_csv(REFERENCE_STORE)

    engine = create_engine('postgresql://airflow:airflow@postgres:5432/airflow')
    current = pd.read_sql('SELECT text, label, pred_label FROM climate_news_data', con=engine)

    definition = DataDefinition(
        classification=[MulticlassClassification(
            target="label", 
            prediction_labels="pred_label"
            )]
            )

    parsed_reference = Dataset.from_pandas(
        reference, 
        data_definition=definition
        )

    parsed_production = Dataset.from_pandas(
        current, 
        data_definition=definition
        )
    
    report = Report(metrics=[
        ClassificationPreset(), 
        DataDriftPreset()])
    
    data_report = report.run(parsed_production, parsed_reference)
    
    data_report.save_html("./data/data_drift_report.html")

with DAG("evidently_monitoring_dag", start_date=datetime(2026, 2, 5), schedule="@once", catchup=False) as dag:
    generate_evidently_report = PythonOperator(task_id="generate_evidently_report", python_callable=_generate_evidently_report)

    generate_evidently_report