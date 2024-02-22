#!/bin/bash

# 停止脚本在遇到错误时继续执行
set -e

# 打印当前执行的dbt命令
set -x

# 检查dbt项目配置
dbt debug

# 运行所有dbt模型
dbt run

# 运行所有定义的测试
dbt test

# 生成项目文档
dbt docs generate

# 在本地服务器上查看项目文档，可通过 http://localhost:8080 访问
dbt docs serve
