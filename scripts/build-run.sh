#!/bin/bash

SCRIPTS_PATH=$(dirname $0)

$SCRIPTS_PATH/build.sh $1
$SCRIPTS_PATH/run.sh