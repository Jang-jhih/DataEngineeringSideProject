from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
from airflow.hooks.postgres_hook import PostgresHook
from airflow.models import Variable
from finlab import data
import finlab
import pandas as pd
import os
from airflow.utils.trigger_rule import TriggerRule


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


# 讀取、轉換和加載數據的函數
def read_transform_and_load_finlab_data(data_type, table_name,otc_date, data_columns, batch_size=10000):

    finlab.login(Variable.get('FINLAB_API_KEY'))
    db_path = os.path.join('/home/jovyan/work', 'finlab_data')
    data.set_storage(data.FileStorage(path=db_path))

    if otc_date:
        with data.universe(market="OTC"):
            # 使用 finlab 的方法獲取數據
            df = data.get(data_type)
            table_name = table_name + '_otc'
    else:
        df = data.get(data_type)




    # 轉換數據為長格式
    df_long = df.stack().reset_index()
    df_long.columns = data_columns

    # 使用 PostgresHook 獲取數據庫連接信息
    pg_hook = PostgresHook(postgres_conn_id='_postgresql')
    engine = pg_hook.get_sqlalchemy_engine()

    with engine.connect() as connection:
        # 建立表格，若不存在則建立
        connection.execute(f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                id SERIAL PRIMARY KEY,
                data JSONB
            );
        """)

        # 清空表格中的現有數據
        connection.execute(f"DELETE FROM {table_name}")

        # 分批次插入數據
        for start in range(0, len(df_long), batch_size):
            end = min(start + batch_size, len(df_long))
            batch_data = df_long.iloc[start:end]
            json_data = batch_data.to_json(orient='records', date_format='iso')
            insert_query = f'INSERT INTO {table_name} (data) VALUES (%s)'
            connection.execute(insert_query, [json_data])



# 創建 DAG
dag = DAG('資料塞postgres',
          default_args=default_args,
          description='A flexible DAG to read, transform, and load different data types from finlab to PostgreSQL',
          schedule_interval='30 20 * * * ',
          catchup=False)

# 為不同類型的數據創建任務
data_types = {
    'price_收盤價': {
        'data_type': 'price:收盤價',
        'table_name': 'price_收盤價',
        'otc_date': False,
        'data_columns': ['date', 'stockid', 'vol']
    },
    'price_收盤價_otc': {
        'data_type': 'price:收盤價',
        'table_name': 'price_收盤價',
        'otc_date': True,
        'data_columns': ['date', 'stockid', 'vol']
    },
    'price_成交筆數_otc': {
        'data_type': 'price:成交筆數',
        'table_name': 'price_成交筆數',
        'otc_date': True,
        'data_columns': ['date', 'stockid', 'vol']
    },
    'price_成交筆數': {
        'data_type': 'price:成交筆數',
        'table_name': 'price_成交筆數',
        'otc_date': False,
        'data_columns': ['date', 'stockid', 'vol']
    },
    'etl_adj_close': {
        'data_type': 'etl:adj_close',
        'table_name': 'etl_adj_close',
        'otc_date': False,
        'data_columns': ['date', 'stockid', 'vol']
    },
    'etl_adj_close_otc': {
        'data_type': 'etl:adj_close',
        'table_name': 'etl_adj_close',
        'otc_date': True,
        'data_columns': ['date', 'stockid', 'vol']
    },
    'etl_adj_high': {
        'data_type': 'etl:adj_high',
        'table_name': 'etl_adj_high',
        'otc_date': False,
        'data_columns': ['date', 'stockid', 'vol']
    },
    'etl_adj_low': {
        'data_type': 'etl:adj_low',
        'table_name': 'etl_adj_low',
        'otc_date': False,
        'data_columns': ['date', 'stockid', 'vol']
    },
}

for data_type, config in data_types.items():
    task = PythonOperator(
        task_id=f'read_transform_load_{data_type}',
        python_callable=read_transform_and_load_finlab_data,
        op_kwargs=config,
        dag=dag,
    )
