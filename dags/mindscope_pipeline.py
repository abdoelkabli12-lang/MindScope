import os
import runpy
from pathlib import Path

import pendulum
from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def clean_data():
    os.chdir(PROJECT_ROOT)
    runpy.run_path(str(PROJECT_ROOT / "src" / "preprocessing" / "cleaning.py"))


def train_evaluate_and_save():
    import joblib

    os.chdir(PROJECT_ROOT)
    results = runpy.run_path(str(PROJECT_ROOT / "src" / "models" / "training.py"))
    model_path = PROJECT_ROOT / "models" / "mindscope_best_model.pkl"
    model_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(results["best_lr_model"], model_path)


with DAG(
    dag_id="mindscope_pipeline",
    start_date=pendulum.datetime(2026, 11, 9, tz="UTC"),
    schedule="@daily",
    catchup=False,
    tags=["mindscope"],
) as dag:
    prepare_data = PythonOperator(
        task_id="clean_data",
        python_callable=clean_data,
    )
    train_and_evaluate = PythonOperator(
        task_id="train_evaluate_and_save",
        python_callable=train_evaluate_and_save,
    )

    prepare_data >> train_and_evaluate
