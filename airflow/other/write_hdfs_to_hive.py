from pyspark.sql import SparkSession
from finlab import data as finlab_data
import pandas as pd

# 初始化 SparkSession，启用对 Hive 的支持
spark = SparkSession.builder \
    .appName("FinlabDataToHive") \
    .enableHiveSupport() \
    .getOrCreate()

# 配置数据类型和相关参数，所有数据类型共用同一基础路径
base_hdfs_path = '/user/hue/finlab/data/'

data_types = {
    'price_closing_price': {
        'data_type': 'price:收盘价',
        'table_name': 'price_closing_price',  
        'otc_date': False,
    },
    'price_closing_price_otc': {
        'data_type': 'price:收盘价',
        'table_name': 'price_closing_price_otc', 
        'otc_date': True,
    },
    'price_transaction_count_otc': {
        'data_type': 'price:成交笔数',
        'table_name': 'price_transaction_count_otc',  
        'otc_date': True,
    },
    'price_transaction_count': {
        'data_type': 'price:成交笔数',
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
        'table_name': 'etl_adj_close_otc',  
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

# 遍历 data_types 字典，取得每种数据并保存到 HDFS 和 Hive
for key, value in data_types.items():
    data_type = value['data_type']
    table_name = value['table_name']
    otc_date = value['otc_date']
    
    # 使用 finlab 的 data.universe 来设置市场类型并获取数据
    with finlab_data.universe(market="OTC" if otc_date else "TWSE"):
        df = finlab_data.get(data_type)
    df.reset_index(inplace=True)
    
    # 将 pandas DataFrame 转换为 Spark DataFrame
    spark_df = spark.createDataFrame(df)
    
    # 构建目标 HDFS 路径，包括文件名（这里使用数据类型的 key 作为文件名的一部分）
    target_hdfs_path = f"{base_hdfs_path}{key}.parquet"
    
    # 将数据保存到 HDFS，使用覆盖模式
    spark_df.write.mode("overwrite").parquet(target_hdfs_path)
    
    # 将数据保存到 Hive 表中，同样使用覆盖模式
    # 注意: 如果 Hive 表的 schema 与 DataFrame 不匹配，这里可能需要额外处理
    spark_df.write.mode("overwrite").saveAsTable(table_name)

# 完成后，关闭 SparkSession
spark.stop()
