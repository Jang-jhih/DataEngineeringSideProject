from airflow import DAG
from airflow.operators.python import PythonVirtualenvOperator
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta
from airflow.utils.dates import days_ago


default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date':  days_ago(1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

def install_dbt_packages():
    import os
    os.system('pip install --upgrade pip')
    os.system('pip install dbt-clickhouse dbt-postgres')

with DAG(
    'dbt_run',
    default_args=default_args,
    description='A simple DAG to run dbt models',
    schedule_interval=timedelta(days=1),
) as dag:

    install_packages = PythonVirtualenvOperator(
        task_id='install_packages',
        python_callable=install_dbt_packages,
        requirements=["dbt-core", "dbt-clickhouse", "dbt-postgres"],
        system_site_packages=False,
    )

    dbt_run = BashOperator(
        task_id='dbt_run',
        bash_command='dbt run --profiles-dir /opt/airflow/dbt_project --project-dir /opt/airflow/dbt_project/dbt_project'
    )
    
    dbt_test = BashOperator(
        task_id='dbt_test',
        bash_command='dbt test --profiles-dir /opt/airflow/dbt_project --project-dir /opt/airflow/dbt_project/dbt_project'  
    )
    
    generate_strategy_tables = BashOperator(
        task_id='generate_strategy_tables',
        bash_command='dbt run-operation generate_strategy_tables --profiles-dir /opt/airflow/dbt_project --project-dir /opt/airflow/dbt_project/dbt_project'
    )

    install_packages >> dbt_run >> dbt_test >> generate_strategy_tables
