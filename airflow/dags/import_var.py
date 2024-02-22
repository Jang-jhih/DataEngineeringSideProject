import json
import os
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.models import Variable
from datetime import datetime
from airflow.utils.dates import days_ago

default_args = {
    'owner': 'airflow',
    'start_date': days_ago(1),
}

def read_env_to_json():
    env_vars = {}
    # 請將這個路徑替換成您的 .env 檔案路徑
    with open('/opt/airflow/.env', 'r') as file:
        for line in file:
            line = line.strip()
            if line and not line.startswith('#'):
                key, value = line.split('=', 1)
                env_vars[key] = value
    # 將轉換後的 JSON 對象匯入 Airflow Variable
    for key, value in env_vars.items():
        Variable.set(key, value)
        os.environ[key] = value

with DAG(
    '環境變數轉換為Airflow變數',
    default_args=default_args,
    description='Convert .env file to JSON and import to Airflow Variables',
    schedule_interval="0 20 * * * ",  # 設定為 None，使其不會按計畫執行
    tags=['system'],
) as dag:

    t1 = PythonOperator(
        task_id='read_env_to_json',
        python_callable=read_env_to_json,
    )

    t1  # 執行任務
