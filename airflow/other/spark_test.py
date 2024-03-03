from hdfs import InsecureClient
import pandas as pd
from io import BytesIO
from finlab import data,login
import os

login(os.environ.get('FINLAB_API_KEY'))


data_types = {
    'price_closing_price': {
        'data_type': 'price:收盤價',
        'table_name': 'price_closing_price',  
        'otc_date': False,

    },
    'price_closing_price_otc': {
        'data_type': 'price:收盤價',
        'table_name': 'price_closing_price', 
        'otc_date': True,

    },
    'price_transaction_count_otc': {
        'data_type': 'price:成交筆數',
        'table_name': 'price_transaction_count_otc',  
        'otc_date': True,

    },
    'price_transaction_count': {
        'data_type': 'price:成交筆數',
        'table_name': 'price_transaction_count',  
        'otc_date': False,

    },
    'etl_adj_close': {
        'data_type': 'etl:adj_close',
        'table_name': 'etl_adj_close',  
        'otc_date': False,

    },
    'etl_adj_close_otc': {
        'data_type': 'etl:adj_close',
        'table_name': 'etl_adj_close',  
        'otc_date': True,

    },
    'etl_adj_high': {
        'data_type': 'etl:adj_high',
        'table_name': 'etl_adj_high',  
        'otc_date': False,

    },
    'etl_adj_low': {
        'data_type': 'etl:adj_low',
        'table_name': 'etl_adj_low',  
        'otc_date': False,

    },
}

for key, value in data_types.items():
    data_type = value['data_type']
    table_name = value['table_name']
    otc_date = value['otc_date']

    with data.universe(market="OTC" if otc_date else "TWSE"):
        finlab_df = data.get(data_type)

    # 建立與 HDFS 的連接
    client = InsecureClient('http://namenode:9870'
                            # , user='hdfs'
                            )



    # 使用 BytesIO 作為中間儲存
    buffer = BytesIO()
    finlab_df.to_parquet(buffer)

    # 重置 buffer 的位置到開頭，以便讀取其內容
    buffer.seek(0)

    client.delete(f'/user/hue/finlab/data/{key}.parquet', recursive=True)
    # 將 buffer 的內容寫入到 HDFS
    client.write(f'/user/hue/finlab/data/{key}.parquet', buffer.read(), overwrite=True)


    from pyspark.sql import SparkSession

# 初始化SparkSession
spark = SparkSession.builder \
    .appName("HDFS to Hive") \
    .config("spark.sql.warehouse.dir", "/user/hive/warehouse") \
    .enableHiveSupport() \
    .getOrCreate()

for key, value in data_types.items():
    table_name = value['table_name']
    
    # 讀取HDFS中的Parquet文件
    parquet_path = f"hdfs://namenode:9000/user/hue/finlab/data/{key}.parquet"
    df = spark.read.parquet(parquet_path)
    
    # 將DataFrame存儲為Hive表
    df.write.mode("overwrite").saveAsTable(table_name)

    print(f"Table {table_name} created in Hive.")

# 關閉SparkSession
spark.stop()
