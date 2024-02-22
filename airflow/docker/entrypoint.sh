#!/bin/bash

# airflow connections add '_mongoid'  --conn-uri 'mongo://mongo:mongo@mongo:27017/'
# airflow connections add '_mysqlid'  --conn-uri 'mysql://root:airflow@mysql:3306/'
# airflow connections add '_postgresql'  --conn-uri 'postgres://postgres:postgres@postgres:5432/stock'
# airflow connections add '_hive'  --conn-uri 'hive://hive@hive-server:10000/default'
# airflow connections add 'hive_default'  --conn-uri 'hive://hive@hive-server:10000/default'


# airflow connections add '_webhdfs' --conn-uri 'webhdfs://namenode:50070'


#
# airflow connections add 'hive_cli_default' \
#     --conn-type 'hive' \
#     --conn-host 'hive-server' \
#     --conn-port 10000 \
#     --conn-login 'hive' \
#     --conn-password 'hive' \
#     --conn-extra '{"use_beeline": true}'

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


# airflow connections add 'hive_default' \
#     --conn-type 'hive_cli' \
#     --conn-host 'hive-server' \
#     --conn-port '10000' \
#     --conn-schema 'default'



airflow connections add '_webhdfs' \
    --conn-type 'hdfs' \
    --conn-host 'namenode' \
    --conn-login 'root' \
    --conn-port '9870'







airflow webserver

# airflow connections test _webhdfs