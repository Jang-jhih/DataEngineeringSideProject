FROM python:3.10-slim-buster

WORKDIR /usr/src/dbt_project

# 安装依赖并清理缓存
RUN apt-get update && \
    apt-get install -y --no-install-recommends git && \  
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    pip install --upgrade pip && \
    pip install dbt-clickhouse \
                dbt-postgres \
                pytz
