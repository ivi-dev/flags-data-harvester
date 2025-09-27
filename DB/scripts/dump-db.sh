#!/bin/bash

# =====================================================================
# Dump the entire MongoDB cluster to a timestamped subdirectory of 
# /var/mongo/dumps.
# 
# The root DB user's credentials, as read from the container's 
# /run/secrets will be used for the dump operation.
# =====================================================================

dump_dir="$DUMP_BASE_DIR/$(date '+%d.%m.%Y-%R:%S-%Z')"

function set-dumps-base-perms () {
	chown -R $SYSTEM_DB_USER $DUMP_BASE_DIR
	chmod 700 -R $DUMP_BASE_DIR
}

# 1. Create the dump base directory if it does not exist
if [ ! -d "/var/mongo/dumps" ]; then
	mkdir -p $DUMP_BASE_DIR
fi
set-dumps-base-perms

# 2. Create a timestamped database dump in the dumps base directory
mongodump --out $dump_dir \
	      --username $(cat $USER_NAME_FILE) \
	      --password $(cat $USER_PASS_FILE) \
	      --authenticationDatabase $AUTH_DB \
	      --ssl \
	      --sslCAFile $SSL_CA_FILE