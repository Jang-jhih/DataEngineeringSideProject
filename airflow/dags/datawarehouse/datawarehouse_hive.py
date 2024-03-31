import os
from airflow import DAG
from airflow.providers.docker.operators.docker import DockerOperator
from datetime import datetime, timedelta
from docker.types import Mount
from airflow.models import Variable

# 尝试从环境变量获取宿主机的工作目录
host_pwd = os.environ.get('HOST_PWD')

# 定义默认参数
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 17),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# DAG 定义
dag = DAG(
    '資料倉儲_hive',
    default_args=default_args,
    description='Run Spark program in Jupyter container',
    schedule_interval='30 20 * * *',
    catchup=False,
    tags=['hive', 'datawarehouse', 'finlab'],
)

# 使用 DockerOperator 运行 Jupyter 中的 Spark 程序
run_spark_job = DockerOperator(
    task_id='run_spark_job_in_jupyter',
    image='zebraking30/finlab-jupyter:latest',
    api_version='auto',
    auto_remove=True,
    command="/bin/bash -c 'python /opt/airflow/other/spark_test.py'",
    network_mode='my_network',
    environment={
        'JAVA_HOME': '/usr/lib/jvm/java-11-openjdk-amd64',
        'SPARK_HOME': '/spark',
        'FINLAB_API_KEY': Variable.get('FINLAB_API_KEY')
        # Set any other required environment variables here
    },
    mount_tmp_dir=False,
    mounts=[Mount(source=f'{host_pwd}/other', target='/opt/airflow/other', type='bind')],
    dag=dag,
)
