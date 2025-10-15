from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

default_args = {
    "owner": "you",
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="daily_stock_etl",
    default_args=default_args,
    start_date=datetime(2025, 1, 1),
    schedule="@daily",
    catchup=False,
) as dag:

    fetch_load = BashOperator(
        task_id="fetch_and_load",
        bash_command="cd /usr/local/airflow/dags && python3 fetch_and_load.py",
        env={
            "ALPHAVANTAGE_KEY": "{{ var.value.alpha_vantage_key }}",
            "GOOGLE_APPLICATION_CREDENTIALS": "/usr/local/airflow/include/credentials/adc.json"
        },
    )
