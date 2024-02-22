# write_hdfs_to_hive.py
from pyspark.sql import SparkSession
import sys

# 接受命令行参数
hdfs_path, hive_table_name = sys.argv[1], sys.argv[2]

spark = SparkSession.builder \
    .appName("Write HDFS Data to Hive") \
    .enableHiveSupport() \
    .getOrCreate()

df = spark.read.parquet(hdfs_path)
df.write.mode("overwrite").saveAsTable(hive_table_name)

spark.stop()
