from airflow import DAG
from airflow.operators.python import PythonOperator
from kafka import KafkaConsumer
from clickhouse_driver import Client
from datetime import datetime, timedelta
import json
# from collections import defaultdict
from airflow.utils.dates import days_ago

TOPIC = 'genetic_algorithm_results'
TABLE_NAME = 'genetic_algorithm_results_v2'

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date':  days_ago(1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

def create_kafka_consumer():
    consumer_conf = {
        'bootstrap_servers': 'broker:29092',
        'group_id': 'clickhouse_sync_v2',
        'auto_offset_reset': 'earliest'
    }
    return KafkaConsumer(TOPIC, **consumer_conf)

def test_connection(ti, test_func):
    try:
        test_func(ti)
    except Exception as e:
        ti.log.error(f"Connection test failed. Error: {str(e)}")
        raise

def test_kafka_connection(ti):
    consumer = create_kafka_consumer()
    subscribed_topics = consumer.topics()
    ti.log.info(f"Kafka connection test successful! Subscribed topics: {subscribed_topics}")
    consumer.close()

def test_clickhouse_connection(ti):
    with Client(host='clickhouse', port=9000) as client:
        result = client.execute('SHOW DATABASES')
        ti.log.info(f"ClickHouse connection test successful! Databases: {result}")

def sync_kafka_to_clickhouse(ti):
    consumer = create_kafka_consumer()

    try:
        with Client(host='clickhouse', port=9000) as client:
            client.execute(f'''
                CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
                    strategy_name String,
                    conditions Array(String),
                    best_conditions Tuple(conditions Array(String), params Map(String, Float64), daily_mean Float64, max_drawdown Float64, daily_sortino Float64),
                    worst_conditions Tuple(conditions Array(String), params Map(String, Float64), daily_mean Float64, max_drawdown Float64, daily_sortino Float64)
                ) ENGINE = MergeTree()
                ORDER BY tuple()
            ''')
            ti.log.info(f"Table {TABLE_NAME} created or already exists.")

            for msg in consumer:
                # 解析消息的值
                value = json.loads(msg.value)
                print(f'Received message: {value}')

                # 將資料插入到 ClickHouse 表中
                client.execute(f'''
                    INSERT INTO {TABLE_NAME} (strategy_name, conditions, best_conditions, worst_conditions)
                    VALUES (%(strategy_name)s, %(conditions)s, %(best_conditions)s, %(worst_conditions)s)
                ''', {
                    'strategy_name': list(value.keys())[0],  # 使用頂層鍵作為策略名稱
                    'conditions': value[list(value.keys())[0]]['conditions'],
                    'best_conditions': tuple(value[list(value.keys())[0]]['best_conditions'].values()),
                    'worst_conditions': tuple(value[list(value.keys())[0]]['worst_conditions'].values())
                })
    finally:
        consumer.close()
        ti.log.info("Kafka consumer closed")

with DAG(
    'clickhouse_kafka_sync',
    default_args=default_args,
    description='Test Kafka and ClickHouse connections and sync data from Kafka topics',
    schedule_interval=None,#timedelta(minutes=30),
    catchup=False,
    tags=['clickhouse', 'kafka'],
) as dag:

    test_kafka = PythonOperator(
        task_id='test_kafka_connection',
        python_callable=test_connection,
        op_kwargs={'test_func': test_kafka_connection},
    )

    test_clickhouse = PythonOperator(
        task_id='test_clickhouse_connection',
        python_callable=test_connection,
        op_kwargs={'test_func': test_clickhouse_connection},
    )

    sync_task = PythonOperator(
        task_id='sync_genetic_algorithm_results_to_clickhouse',
        python_callable=sync_kafka_to_clickhouse,
    )

    test_kafka >> test_clickhouse >> sync_task
