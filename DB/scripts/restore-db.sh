#!/bin/bash

# =====================================================================
# Restore the entire MongoDB cluster from the specified dump.
# 
# If a dump directory is not specified on the command-line
# the restore will use the latest dump in /var/mongo/dumps.
# 
# The root user's credentials, as read from the container's 
# /run/secrets are used for the restore operation.
#
# -------------------
# Params:
# -------------------
# --in - An optional dump directory to restore from. 
#        If not specified, the latest dump in /var/mongo/dumps
#        will be used.
# =====================================================================

dump=
to_assign=

# 1. Parse command-line parameters
for arg in $@; do
	if [ ${arg:0:2} == "--" ]; then 
		option=${arg:2}
		if [ $option == "dump" ]; then
			to_assign="dump"
			continue
		fi
	fi
	case $to_assign in
		"dump")
			dump=$arg;;
	esac
done

# 2. Establish the dump's input directory
latest_dump=
if [ "$dump" == "" ]; then
    if [ ! -d "/var/mongo/dumps" ]; then
        echo "ERROR: No dumps directory found at /var/mongo/dumps." 
        exit 1
    fi
    latest_dump=$(ls -t /var/mongo/dumps | head -n 1)
    if [ "$latest_dump" == "" ]; then
        echo "ERROR: No dumps found in /var/mongo/dumps." 
        exit 1
    fi
    dump="/var/mongo/dumps/$latest_dump"
else
    if [ ! -d "$dump" ]; then
        echo "ERROR: Specified dump directory $dump not found." 
        exit 1
    fi
fi

# 3. Restore the cluster from the specified dump directory
mongorestore --dir $dump \
	         --username $(cat /run/secrets/db-root-user) \
	         --password $(cat /run/secrets/db-root-pass) \
	         --authenticationDatabase admin \
	         --ssl \
	         --sslCAFile /etc/ssl/certs/flags/cert.crt