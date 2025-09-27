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
# --dump - An optional dump's name (a subdirectory of /var/mongo/dumps) 
# 	       to restore from. If not specified, the latest dump in 
# 		   /var/mongo/dumps will be used.
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
    if [ ! -d "$DUMP_BASE_DIR" ]; then
        echo "ERROR: No dumps base directory found at $DUMP_BASE_DIR." 
        exit 1
    fi
    latest_dump=$(ls -t "$DUMP_BASE_DIR" | head -n 1)
    if [ "$latest_dump" == "" ]; then
        echo "ERROR: No database dumps found in $DUMP_BASE_DIR." 
        exit 1
    fi
    dump="$DUMP_BASE_DIR/$latest_dump"
else
    if [ ! -d "$DUMP_BASE_DIR/$dump" ]; then
        echo "ERROR: Specified dump directory $dump not found." 
        exit 1
    fi
fi

# 3. Restore the cluster from the specified dump directory
mongorestore --dir $dump \
	         --username $(cat $USER_NAME_FILE) \
	         --password $(cat $USER_PASS_FILE) \
	         --authenticationDatabase $AUTH_DB \
	         --ssl \
	         --sslCAFile $SSL_CA_FILE