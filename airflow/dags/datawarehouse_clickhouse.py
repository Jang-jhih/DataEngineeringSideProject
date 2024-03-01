from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.models import Variable
from datetime import datetime, timedelta
import pandas as pd
import logging
from clickhouse_driver import Client
import finlab
from finlab import data
from airflow.utils.dates import days_ago

# 定義預設參數
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': days_ago(1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# DAG 定義
dag = DAG(
    '資料倉儲_clickhouse',
    default_args=default_args,
    description='一個靈活的DAG，用於從finlab讀取、轉換和加載不同的數據類型到ClickHouse',
    schedule_interval='30 20 * * *',
    catchup=False,
    tags=['clickhouse', 'datawarehouse', 'finlab'],
)

def upload_data_to_clickhouse(table_name, data_type, otc_date, **kwargs):
    logging.info("開始執行 read_transform_and_load_finlab_data_to_clickhouse")
    # 假設您已有 finlab 數據獲取的邏輯


    # 登錄 finlab
    logging.info("登錄 finlab")
    finlab.login(Variable.get('FINLAB_API_KEY'))


    # 獲取數據
    logging.info(f"獲取數據: {data_type}")
    with data.universe(market="OTC" if otc_date else "TWSE"):
        df = data.get(data_type)
    df.reset_index(inplace=True)

    df_long = pd.melt(df, id_vars=['date'], var_name='symbol', value_name='price')

    # 這裡僅示範如何連接 ClickHouse 並插入數據
    client = Client(host='clickhouse', port=9000)

    # 轉換數據為元組列表
    tuples = list(df_long.itertuples(index=False, name=None))

    # 創建表格（如果尚不存在）
    create_table_query = f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
        date Date,
        symbol String,
        price Float32
    ) ENGINE = MergeTree() ORDER BY (date, symbol)
    """
    try:
        client.execute(create_table_query)
    except Exception as e:
        logging.error(f"创建表格 {table_name} 失败: {e}")
        raise

    # 插入数据
    insert_query = f"INSERT INTO {table_name} VALUES"
    try:
        client.execute(insert_query, tuples)
        logging.info(f"数据成功上传到 {table_name}")
    except Exception as e:
        logging.error(f"插入数据到 {table_name} 失败: {e}")
        raise

# 配置數據類型和相關參數
data_types = {
    'price_closing_price': {
        'data_type': 'price:收盤價',
        'table_name': 'price_closing_price',  
        'otc_date': False,
        # 'hdfs_path': '/user/hue/finlab/data/price_closing_price'
    },
    'price_closing_price_otc': {
        'data_type': 'price:收盤價',
        'table_name': 'price_closing_price', 
        'otc_date': True,
        # 'hdfs_path': '/user/hue/finlab/data/price_closing_price_otc'
    },
    'price_transaction_count_otc': {
        'data_type': 'price:成交筆數',
        'table_name': 'price_transaction_count_otc',  
        'otc_date': True,
        # 'hdfs_path': '/user/hue/finlab/data/price_transaction_count_otc'
    },
    'price_transaction_count': {
        'data_type': 'price:成交筆數',
        'table_name': 'price_transaction_count',  
        'otc_date': False,
        # 'hdfs_path': '/user/hue/finlab/data/price_transaction_count'
    },
    'etl_adj_close': {
        'data_type': 'etl:adj_close',
        'table_name': 'etl_adj_close',  
        'otc_date': False,
        # 'hdfs_path': '/user/hue/finlab/data/etl_adj_close'
    },
    'etl_adj_close_otc': {
        'data_type': 'etl:adj_close',
        'table_name': 'etl_adj_close',  
        'otc_date': True,
        # 'hdfs_path': '/user/hue/finlab/data/etl_adj_close_otc'
    },
    'etl_adj_high': {
        'data_type': 'etl:adj_high',
        'table_name': 'etl_adj_high',  
        'otc_date': False,
        # 'hdfs_path': '/user/hue/finlab/data/etl_adj_high'
    },
    'etl_adj_low': {
        'data_type': 'etl:adj_low',
        'table_name': 'etl_adj_low',  
        'otc_date': False,
        # 'hdfs_path': '/user/hue/finlab/data/etl_adj_low'
    },
}


for data_key, config in data_types.items():
    task_id = f"upload_{config['table_name']}_{config['otc_date']}_to_clickhouse"

    upload_task = PythonOperator(
        task_id=task_id,
        python_callable=upload_data_to_clickhouse,
        op_kwargs={
            'table_name': config['table_name'],
            'data_type': config['data_type'],
            'otc_date': config['otc_date']
        },
        dag=dag,
    )
