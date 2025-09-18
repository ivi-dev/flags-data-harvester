#!/bin/bash

# ================================================
# Create MongoDB-required files and directories,
# if missing.
# ================================================

# 1. Create the mongod log file if it doesn't exist
if [ ! -f "$LOG_PATH" ]; then
    echo "Creating the MongoDB log file at $LOG_PATH"
    touch $LOG_PATH
    chown $SYSTEM_DB_USER:$SYSTEM_DB_GROUP $LOG_PATH
    chmod 700 $LOG_PATH
fi

# 2. Create the DB data directory if it doesn't exist
if [ ! -d "$DATA_PATH" ]; then
    echo "Creating the MongoDB data directory at $DATA_PATH"
    mkdir -p $DATA_PATH
fi
chown -R $SYSTEM_DB_USER:$SYSTEM_DB_GROUP $DATA_PATH
chmod -R 700 $DATA_PATH

# 3. Create the mongod pid file if it doesn't exist
if [ ! -f "$PID_PATH" ]; then
    echo "Creating the MongoDB pid file at $PID_PATH"
    parent_dir=$(dirname "$PID_PATH")
    mkdir -p $parent_dir
    chown $SYSTEM_DB_USER:$SYSTEM_DB_GROUP $parent_dir
    chmod 700 $parent_dir
    touch $PID_PATH
    chown $SYSTEM_DB_USER:$SYSTEM_DB_GROUP $PID_PATH
    chmod 700 $PID_PATH
fi