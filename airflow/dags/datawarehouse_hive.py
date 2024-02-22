from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from airflow.providers.apache.hive.hooks.hive import HiveServer2Hook
from airflow.providers.apache.hdfs.hooks.webhdfs import WebHDFSHook
from airflow.models import Variable
from datetime import datetime, timedelta
import pandas as pd
import os
import logging
import finlab
from finlab import data

# 定義預設參數
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 17),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# DAG 定義
dag = DAG(
    '更新hive',
    default_args=default_args,
    description='A flexible DAG to read, transform, and load different data types from finlab to HDFS and Hive',
    schedule_interval='30 20 * * *',
    catchup=False,
    tags=['hdfs', 'finlab', 'hive'],
)

# Task 定義
# 上傳 Parquet 文件到 HDFS
def upload_parquet_to_hdfs(table_name, hdfs_path, data_type, otc_date, ti, **kwargs):

    logging.info("開始執行 read_transform_and_load_finlab_data_to_parquet")

    # 登錄 finlab
    logging.info("登錄 finlab")
    finlab.login(Variable.get('FINLAB_API_KEY'))


    # 獲取數據
    logging.info(f"獲取數據: {data_type}")
    with data.universe(market="OTC" if otc_date else "TWSE"):
        df = data.get(data_type)

    # 將數據上傳到 XCom
    ti.xcom_push(key='data_sample', value=df.to_json())
    # 組合 Hive 表名
    table_name = f"{table_name}_{'otc' if otc_date else 'twse'}"
    logging.info(f"生成的 Hive 表名為: {table_name}")

    # 轉換成 Parquet 並上傳至 HDFS
    parquet_file = f'/tmp/{table_name}.parquet'

    df.to_parquet(parquet_file)

    # 模擬的上傳邏輯，需要替換成實際的上傳代碼
    logging.info(f"Uploading {table_name} to HDFS path: {hdfs_path}")
    # 假設已經在本地生成了 Parquet 文件
    parquet_file = f'/tmp/{table_name}.parquet'
    # 使用 WebHDFSHook 來上傳文件
    hdfs_hook = WebHDFSHook(webhdfs_conn_id='_webhdfs')
    hdfs_hook.load_file(parquet_file, hdfs_path, overwrite=True)

# 檢查 HDFS 路徑
def check_and_create_hdfs_path(hdfs_path, **kwargs):
    # 使用 WebHDFSHook 來檢查路徑
    logging.info(f"Checking and potentially creating HDFS path: {hdfs_path}")
    hdfs_hook = WebHDFSHook(webhdfs_conn_id='_webhdfs')
    client = hdfs_hook.get_conn()
    if not client.status(hdfs_path, strict=False):
        client.makedirs(hdfs_path)
        logging.info(f"Created HDFS path: {hdfs_path}")
    else:
        logging.info(f"HDFS path already exists: {hdfs_path}")

# 建立 Hive 表
def create_hive_table(table_name, hdfs_path, data_type, otc_date, **kwargs):
    hive_hook = HiveServer2Hook(hiveserver2_conn_id='hive_cli_default')
    # 构建task_id，逻辑需要与设置PythonOperator的task_id时相同
    market_suffix = 'otc' if otc_date else 'twse'
    task_id_for_upload = f"upload_{table_name}_{market_suffix}_to_hdfs"

    # 从XCom拉取数据
    data_sample_json = kwargs['ti'].xcom_pull(task_ids=task_id_for_upload, key='data_sample')
    data_sample = pd.read_json(data_sample_json)
    
    def infer_data_type(value):
        if pd.isnull(value):
            return 'DOUBLE'  # 對於NaN值，假設欄位類型為DOUBLE
        try:
            float(value)
            return 'DOUBLE'
        except ValueError:
            return 'STRING'

    # 生成CREATE TABLE語句
    create_table_stmt = f"CREATE EXTERNAL TABLE IF NOT EXISTS {table_name} (\n"
    for column in data_sample.columns:
        safe_column = f"`{column}`" if column[0].isdigit() else column
        data_type = infer_data_type(data_sample[column][0])
        create_table_stmt += f"    {safe_column} {data_type},\n"
    create_table_stmt = create_table_stmt.rstrip(',\n') + f"\n) STORED AS PARQUET LOCATION '{hdfs_path}'"

    try:
        hive_hook.run(sql=create_table_stmt)
    except Exception as e:
        logging.error(f"Error creating Hive table {table_name}: {e}")
        raise


data_types = {
    'price_closing_price': {
        'data_type': 'price:收盤價',
        'table_name': 'price_closing_price',  # 将中文更改为英文
        'otc_date': False,
        'hdfs_path': '/user/hue/finlab/data/price_closing_price'
    },
    'price_closing_price_otc': {
        'data_type': 'price:收盤價',
        'table_name': 'price_closing_price', 
        'otc_date': True,
        'hdfs_path': '/user/hue/finlab/data/price_closing_price_otc'
    },
    'price_transaction_count_otc': {
        'data_type': 'price:成交筆數',
        'table_name': 'price_transaction_count_otc',  
        'otc_date': True,
        'hdfs_path': '/user/hue/finlab/data/price_transaction_count_otc'
    },
    'price_transaction_count': {
        'data_type': 'price:成交筆數',
        'table_name': 'price_transaction_count',  
        'otc_date': False,
        'hdfs_path': '/user/hue/finlab/data/price_transaction_count'
    },
    'etl_adj_close': {
        'data_type': 'etl:adj_close',
        'table_name': 'etl_adj_close',  
        'otc_date': False,
        'hdfs_path': '/user/hue/finlab/data/etl_adj_close'
    },
    'etl_adj_close_otc': {
        'data_type': 'etl:adj_close',
        'table_name': 'etl_adj_close',  
        'otc_date': True,
        'hdfs_path': '/user/hue/finlab/data/etl_adj_close_otc'
    },
    'etl_adj_high': {
        'data_type': 'etl:adj_high',
        'table_name': 'etl_adj_high',  
        'otc_date': False,
        'hdfs_path': '/user/hue/finlab/data/etl_adj_high'
    },
    'etl_adj_low': {
        'data_type': 'etl:adj_low',
        'table_name': 'etl_adj_low',  
        'otc_date': False,
        'hdfs_path': '/user/hue/finlab/data/etl_adj_low'
    },
}




for data_key, config in data_types.items():
    market_suffix = 'otc' if config['otc_date'] else 'twse'  # 為不同市場添加後綴

    upload_task_id = f"upload_{config['table_name']}_{market_suffix}_to_hdfs"
    check_path_task_id = f"check_hdfs_path_{config['table_name']}_{market_suffix}"
    create_table_task_id = f"create_hive_table_{config['table_name']}_{market_suffix}"

    upload_task = PythonOperator(
        task_id=upload_task_id,
        python_callable=upload_parquet_to_hdfs,
        op_kwargs={
            'table_name': config['table_name'],
            'hdfs_path': config['hdfs_path'],
            'data_type': config['data_type'],
            'otc_date': config['otc_date']
        },
        dag=dag,
    )

    check_path_task = PythonOperator(
        task_id=check_path_task_id,
        python_callable=check_and_create_hdfs_path,
        op_kwargs={'hdfs_path': config['hdfs_path']},
        dag=dag,
    )

    create_table_task = SparkSubmitOperator(
        task_id=create_table_task_id,
        application="/opt/airflow/other/write_hdfs_to_hive.py",  # Spark作业脚本的路径
        name="Write_HDFS_to_Hive",
        conn_id="spark_default",  # Spark连接ID，需在Airflow中预先配置
        application_args=[config['hdfs_path'], f"{config['table_name']}_{market_suffix}"],
        verbose=True,
        dag=dag,
        conf={
            'spark.driver.extraJavaOptions': '--add-opens java.base/java.nio=ALL-UNNAMED',
            'spark.executor.extraJavaOptions': '--add-opens java.base/java.nio=ALL-UNNAMED'
        }
    )

    # 設置任務依賴
    upload_task >> check_path_task >> create_table_task
