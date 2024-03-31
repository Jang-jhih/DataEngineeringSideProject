from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.utils.dates import days_ago
from datetime import timedelta
from airflow.models import Variable
import os

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': days_ago(1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

def run_python_script(script_path):
    '''
    執行 Python 腳本

    Parameters
    ----------
    script_path : str
        Python 腳本路徑

    '''
    print(f"執行 Python 腳本：{script_path}")
    exec(open(script_path).read())

def execute_python_scripts(**kwargs):
    '''
    執行 /home/jovyan/work/GA 中的所有 Python 腳本
    
    '''
    
    script_dir = os.path.join(Variable.get('STRATEGY_PATH'), 'GA')

    for script in os.listdir(script_dir):
        if script.endswith(".py"):
            script_path = os.path.join(script_dir, script)
            run_python_script(script_path)

dag = DAG(
    '基因演算法',
    default_args=default_args,
    description='Execute Python scripts in /home/jovyan/work/GA',
    tags=['strategy'],
    schedule_interval=None,
)

execute_scripts_task = PythonOperator(
    task_id='基因演算法執行',
    python_callable=execute_python_scripts,
    provide_context=True,
    dag=dag,
)