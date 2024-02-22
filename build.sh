#!/bin/bash

# 函數：構建並推送 Docker 映像
build_and_push() {
  local service_name=$1
  local image_name=$2
  local dockerfile_name=$3

  # 構建映像
  echo "Building image for service: $service_name..."
  docker build --no-cache  -f $dockerfile_name -t $image_name . || exit 1
        #  --no-cache  \
        

  # 推送映像到 Docker Hub
  echo "Pushing image: $image_name to Docker Hub..."
  docker push "$image_name" || exit 1
}

# 登錄 Docker Hub
echo "Logging in to Docker Hub..."
docker login || exit 1

# # 構建並推送 jupyter 映像
# build_and_push "jupyter" "zebraking30/finlab-jupyter:latest" "Dockerfile.jupyter"

# # 構建並推送 magic 映像
# build_and_push "magic" "zebraking30/finlab-mageai:latest" "Dockerfile.magai"

# 構建並推送 airflow 映像
build_and_push "airflow" "zebraking30/finlab-airflow:latest" "Dockerfile.airflow"

echo "All images pushed to Docker Hub successfully!"
