#!/bin/bash


airflow connections add 'hive_server_default' \
    --conn-type 'hiveserver2' \
    --conn-host 'hive-server' \
    --conn-login 'hive' \
    --conn-password 'hive' \
    --conn-port '10000' \
    --conn-extra '{
        "use_beeline": true,
        "authMechanism": "KERBEROS",
        "kerberos_service_name": "hive",
    }'



airflow connections add '_webhdfs' \
    --conn-type 'hdfs' \
    --conn-host 'namenode' \
    --conn-login 'root' \
    --conn-port '9870'





# airflow connections add clickhouse_default\
#                     --conn-type clickhouse\
#                     --conn-host clickhouse\
#                     --conn-port 9000\
#                     --conn-schema default\
#                     --conn-login default\
#             --conn-extra '{"secure": false}'

airflow connections add kafka_default\
            --conn-type apache_kafka\
            --conn-extra '{"bootstrap.servers":"broker:29092","group.id": "clickhouse_sync","auto.offset.reset": "earliest"}'


airflow webserver

