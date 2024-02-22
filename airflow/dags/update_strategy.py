from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
from airflow.utils.dates import days_ago
import os
import sys
from airflow.models import Variable
import finlab
from finlab import data
from airflow.sensors.external_task_sensor import ExternalTaskSensor
# Import your modules
# import cfg
# from message import Message, Get_Strategy_Ifo

# DAG's default arguments
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': days_ago(1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Define the DAG
dag = DAG(
    '上傳策略結果到discord',
    default_args=default_args,
    description='上傳策略結果到discord',
    # schedule_interval=timedelta(days=1),
    tags=['discord'],
)

# Define the task
def run_script():
    finlab.login(Variable.get('FINLAB_API_KEY'))
    sys.path.append(Variable.get('CONDITION_PATH'))
    from message import Message, Get_Strategy_Ifo

    webhook_url = Variable.get('For_jacob_pred')
    Doc = Variable.get('Strategy_DOC')
    strategy_name = 'Composit_Program'

    report = Get_Strategy_Ifo(strategy_name)
    mes = Message(webhook_url, strategy_name, doc=Doc)

    df = report.get_strategy_date()
    entry_time = df['進場時間'].iloc[0]
    entry_time = datetime.strptime(entry_time, '%Y-%m-%d')
    today = datetime.now().date()
    is_today = entry_time.date() == today
    if is_today:
        folder = os.path.join(Variable.get('CONDITION_PATH'), 'combie_strategy')
        text = report.show_report(folder)
        mes.send_strategy_date(df, content=f'{text}')

# 使用 ExternalTaskSensor 等待 strategy_execution_dag 完成
# wait_for_strategy_execution = ExternalTaskSensor(
#     task_id='wait_for_strategy_execution',
#     external_dag_id='strategy_execution_dag',  # 要等待的DAG ID
#     external_task_id=None,  # None 表示等待整個DAG完成
#     execution_delta=timedelta(hours=1),  # 根據需要調整時間差
#     dag=dag,
# )

run_task = PythonOperator(
    task_id='run_composit_program',
    python_callable=run_script,
    dag=dag
)

# 設置任務依賴
# wait_for_strategy_execution >> 
run_task

