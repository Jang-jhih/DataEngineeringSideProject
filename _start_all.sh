#!/bin/bash

#stop all containers
docker stop $(docker ps -a -q)
docker rm $(docker ps -a -q)
docker rmi $(docker images -q)

# sudo chmod -R 777 /var/run/docker.sock

docker network rm my_network
docker network create my_network


#volume
docker compose -f ./volume/docker-compose.yml up -d

# airflow
docker compose -f ./airflow/docker-compose.yml up -d

# jupyter
docker compose -f ./jupyter/docker-compose.yml up -d

#superset
docker compose -f ./superset/docker-compose.yml up -d

#datahub
docker compose -f ./datahub/docker-compose.yml up -d



# sudo service docker restart
# docker compose logs -f spark-worker-1
# sudo service docker restart


# 