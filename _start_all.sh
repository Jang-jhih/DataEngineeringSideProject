#!/bin/bash

docker network create my_network


#volume
docker compose -f ./volume/docker-compose.yml up -d

# airflow
docker compose -f ./airflow/docker-compose.yml up -d

# # jupyter
docker compose -f ./jupyter/docker-compose.yml up -d

#superset
docker compose -f ./superset/docker-compose.yml up -d


#stop all containers
docker stop $(docker ps -a -q)
docker rm $(docker ps -a -q)
docker rmi $(docker images -q)

docker network rm my_network
docker network create my_network
# sudo service docker restart
# docker compose logs -f spark-worker-1
# sudo service docker restart


# sudo chmod -R 777 /var/run/docker.sock