#!/bin/bash

CONTAINER_NAME=flags-db

docker rm -f $CONTAINER_NAME
docker run -d \
       --name $CONTAINER_NAME \
       -e MONGO_INITDB_ROOT_USERNAME=root \
       -e MONGO_INITDB_ROOT_PASSWORD=root \
       -p 27017:27017 \
       --mount type=volume,src=flags-db-config,dst=/data/configdb \
       --mount type=volume,src=flags-db-data,dst=/data/db \
       $CONTAINER_NAME:latest
docker network connect flags $CONTAINER_NAME