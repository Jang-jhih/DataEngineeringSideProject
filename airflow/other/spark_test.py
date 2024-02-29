from pyspark.sql import SparkSession

# 创建支持Hive的SparkSession
spark = SparkSession.builder \
    .master("spark://spark-master:7077") \
    .appName("Read HDFS Data and Write to Hive") \
    .enableHiveSupport() \
    .config("spark.sql.warehouse.dir", "hdfs://namenode:9000/user/hive/warehouse") \
    .config("hive.metastore.uris", "thrift://hive-metastore:9083") \
    .getOrCreate()

spark.sql("DROP TABLE IF EXISTS your_hive_table_name")


# 从HDFS读取数据
hdfs_path = "hdfs://namenode:9000/user/hue/finlab/data/etl_adj_high"
df = spark.read.parquet(hdfs_path)

# 将数据写入Hive表
df.write.mode("overwrite").saveAsTable("your_hive_table_name")

spark.stop()
