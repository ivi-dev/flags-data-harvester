#!/bin/bash

CONTAINER_NAME=flags-data-harvester

docker rm -f $CONTAINER_NAME
docker run -d --name $CONTAINER_NAME $CONTAINER_NAME:latest
docker network connect flags $CONTAINER_NAME