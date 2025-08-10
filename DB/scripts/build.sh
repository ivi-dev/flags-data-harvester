#!/bin/bash

IMG_NAME=flags-db:latest

docker image rm -f $IMG_NAME
docker build -t $IMG_NAME $1