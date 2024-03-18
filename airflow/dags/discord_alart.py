from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.models import Variable
from datetime import datetime, timedelta
import os
from airflow.utils.dates import days_ago

# Set environment variable for all tasks
os.environ['OPENAI_API_KEY'] = Variable.get('OPENAI_API_KEY')

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': days_ago(1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG('discord_提示', 
          default_args=default_args, 
          schedule_interval='30 20 * * 1-5',
          tags=['discord'])


def common_setup():
    import sys
    sys.path.append(Variable.get('CONDITION_PATH'))
    
    import finlab
    import os
    from finlab import data

    today = datetime.now().strftime("%Y-%m-%d")
    start_date_obj = datetime.strptime(today, '%Y-%m-%d')
    days_ago = start_date_obj - timedelta(days=120)
    days_ago_str = days_ago.strftime('%Y-%m-%d')
    finlab.login(Variable.get('FINLAB_API_KEY'))
    db_path = os.path.join('/home/jovyan/work', 'finlab_data')
    data.set_storage(data.FileStorage(path=db_path))


    from plot import ChartPlotter
    from message import Message

    return ChartPlotter, Message, days_ago_str,finlab,data

def task1(*args, **kwargs):
    ChartPlotter, Message, days_ago_str,finlab,data = common_setup()
    chart = ChartPlotter(start_date=days_ago_str, end_date=None)
    window = 10
    webhook_url = Variable.get('Warning_pred')
    deviation_doc = Variable.get('Deviation_DOC')

    try:
        deviation, content, fig = chart.plot_deviation(window=window, save_image=True)
        if deviation:
            Message(webhook_url, doc=deviation_doc).send_image_message(obj=deviation, content=content)
    except Exception as e:
        print(f"Error in task1: {e}")

def task2(*args, **kwargs):
    ChartPlotter, Message, days_ago_str,finlab,data = common_setup()
    chart = ChartPlotter(start_date=days_ago_str, end_date=None)
    window = 10
    webhook_url = Variable.get('Warning_pred')
    rsi_doc = Variable.get('RSI_DOC')

    try:
        rsi_image_path, content, fig = chart.rsi_rate(window=window, save_image=True)
        if rsi_image_path:
            Message(webhook_url, doc=rsi_doc).send_image_message(obj=rsi_image_path, content=content)
    except Exception as e:
        print(f"Error in task2: {e}")


def task3(*args, **kwargs):
    ChartPlotter, Message, days_ago_str,finlab,data = common_setup()
    chart = ChartPlotter(start_date=days_ago_str, end_date=None)
    window = 10
    webhook_url = Variable.get('Warning_pred')
    # rsi_doc = Variable.get('RSI_DOC')

    try:
        volatility_image_path, content, fig = chart.volatility(window=window, save_image=True)
        if volatility_image_path:
            Message(webhook_url, doc="").send_image_message(obj=volatility_image_path, content=content)
    except Exception as e:
        print(f"Error in task2: {e}")



def task4(*args, **kwargs):
    ChartPlotter, Message, days_ago_str,finlab,data = common_setup()
    chart = ChartPlotter(start_date=days_ago_str, end_date=None, gpt_model='gpt-4')
    webhook_url = Variable.get('Stock_Market_pred')
    adls_doc = Variable.get('ADLS_DOC')

    try:
        adls_image_path, content = chart.plot_adl_data(benchmark=1, ma_range=[5, 10, 20, 40], save_image=True)
        if adls_image_path:
            Message(webhook_url, doc=adls_doc).send_image_message(obj=adls_image_path, content=content)
    except Exception as e:
        print(f"Error in task3: {e}")

task_1 = PythonOperator(task_id='deviation', python_callable=task1, dag=dag)
task_2 = PythonOperator(task_id='RSI', python_callable=task2, dag=dag)
task_3 = PythonOperator(task_id='volatility', python_callable=task3, dag=dag)
task_4 = PythonOperator(task_id='adls', python_callable=task3, dag=dag)

task_1 >> task_2 >> task_3 >> task_4
