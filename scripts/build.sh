#!/bin/bash

IMG_NAME=flags-data-harvester:latest

docker image rm -f $IMG_NAME
docker build -t $IMG_NAME $1