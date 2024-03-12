#!/bin/bash

# 定義 Docker Compose 文件所在的目錄
directories=(
    "volume"
    "airflow"
    "superset"
    "jupyter"
    "hadoop"
    "datahub"
    "queue_console"
    
)

# 在每個目錄中運行 docker-compose up -d
for dir in "${directories[@]}"; do
    echo "Starting services in $dir..."
    docker compose -f "$dir/docker-compose.yml" up -d
    if [ $? -ne 0 ]; then
        echo "Failed to start services in $dir"
        exit 1
    fi
done

echo "All services started successfully."
