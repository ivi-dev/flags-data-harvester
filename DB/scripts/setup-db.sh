#!/bin/bash

# ================================================
# Create MongoDB-required files and directories,
# if missing and trust self-signed SSL 
# certificates.
# ================================================

# 1. Create the mongod log file if it doesn't exist
if [ ! -f "$LOG_PATH" ]; then
    echo "Creating the MongoDB log file at $LOG_PATH"
    touch $LOG_PATH
    chown $SYSTEM_DB_USER $LOG_PATH
    chmod 700 $LOG_PATH
fi

# 2. Create the DB data directory if it doesn't exist
if [ ! -d "$DATA_PATH" ]; then
    echo "Creating the MongoDB data directory at $DATA_PATH"
    mkdir -p $DATA_PATH
fi
chown -R $SYSTEM_DB_USER $DATA_PATH
chmod -R 700 $DATA_PATH

# 3. Create the DB dumps base directory if it doesn't exist
if [ ! -d "$DUMP_BASE_DIR" ]; then
    echo "Creating the MongoDB dumps base directory at $DUMP_BASE_DIR"
    mkdir -p $DUMP_BASE_DIR
fi
chown -R $SYSTEM_DB_USER $DUMP_BASE_DIR
chmod -R 700 $DUMP_BASE_DIR

# 4. Create the mongod pid file if it doesn't exist
if [ ! -f "$PID_PATH" ]; then
    echo "Creating the MongoDB pid file at $PID_PATH"
    parent_dir=$(dirname "$PID_PATH")
    mkdir -p $parent_dir
    chown $SYSTEM_DB_USER $parent_dir
    chmod 700 $parent_dir
    touch $PID_PATH
    chown $SYSTEM_DB_USER $PID_PATH
    chmod 700 $PID_PATH
fi

# 5. Trust self-signed SSL certificate
cp $ROOT_CA_PATH $SYSTEM_CA_CERTS_PATH/flags-root-ca.crt
update-ca-certificates