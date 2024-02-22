#!/bin/bash


airflow standalone
# 初始化 Airflow
airflow db migrate



# 創建 Airflow 使用者
airflow users create \
    --username jacob \
    --firstname jacob \
    --lastname jacob \
    --role Admin \
    --email jacob@gmail.com \
    --password jacob


# 启动 Web 服务器和调度器
# 注意: 这里需要并行运行 webserver 和 scheduler
airflow scheduler
