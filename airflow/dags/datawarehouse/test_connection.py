from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.providers.apache.hdfs.hooks.webhdfs import WebHDFSHook
from datetime import datetime, timedelta

# 定義 DAG 的默認參數
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 25),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# 定義 DAG
dag = DAG(
    '測試hive與webhdfs連線',
    default_args=default_args,
    description='DAG for testing Hive Metastore connection',
    schedule_interval=None,  # 此 DAG 不會按計劃執行，只在手動觸發時運行
    catchup=False,
    tags=['test', 'conncetion'],
)

# 定義用於測試 WebHDFS 連線的函數
def test_webhdfs_connection():
    try:
        hook = WebHDFSHook(webhdfs_conn_id='_webhdfs')
        client = hook.get_conn()
        print("Connected to WebHDFS successfully.")
    except Exception as e:
        raise Exception("Failed to connect to WebHDFS: " + str(e))

# 定義用於測試 Hive Metastore 連線的函數
from airflow.providers.apache.hive.hooks.hive import HiveCliHook

def test_hive_metastore_connection():
    hive_hook = HiveCliHook('hive_cli_default')  # 使用您的连接 ID
    try:
        # 执行一个测试查询
        query = "SHOW TABLES"
        result = hive_hook.run_cli(hql=query)
        if isinstance(result, (str, bytes)):
            print("连接成功。查询结果：")
            print(result)
        else:
            print("连接成功，但返回类型不是字符串或字节。")
            print("返回类型:", type(result))
    except Exception as e:
        print(f"连接失败：{e}")

# 創建 PythonOperator 任務
test_webhdfs_connection_task = PythonOperator(
    task_id='test_webhdfs_connection',
    python_callable=test_webhdfs_connection,
    dag=dag,
)

test_hive_metastore_connection_task = PythonOperator(
    task_id='test_hive_metastore_connection',
    python_callable=test_hive_metastore_connection,
    dag=dag,
)

# 設定 DAG 結構
test_webhdfs_connection_task >> test_hive_metastore_connection_task
