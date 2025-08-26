#!/bin/bash

# =====================================================================
# Dump the entire MongoDB cluster to a timestamped directory 
# in the specified base directory.
# 
# If an output directory is not specified on the command-line
# the dump will be placed into a default base directory at 
# /var/mongo/dumps.
# 
# The root user's credentials, as read from the container's 
# /run/secrets are used for the dump operation.
#
# -------------------
# Params:
# -------------------
# --out - An optional base directory to place the dump into. 
#         If not specified, the dump will be placed into 
#	      /var/mongo/dumps.
# =====================================================================

out=
dump_dir="$(date '+%d.%m.%Y-%R:%S-%Z')"
to_assign=

# 1. Parse command-line parameters
for arg in $@; do
	if [ ${arg:0:2} == "--" ]; then 
		option=${arg:2}
		if [ $option == "out" ]; then
			to_assign="out"
			continue
		fi
	fi
	case $to_assign in
		"out")
			out=$arg;;
	esac
done

# 2. Establish the dump's output directory
[ "$out" == "" ] && out="/var/mongo/dumps/$dump_dir"

# 3. Create the dump's output directory if necessary
[ ! -d $out ] && mkdir -p $out

# 4. Create a database dump and place it in the output directory
mongodump --out $out \
	      --username $(cat /run/secrets/db-root-user) \
	      --password $(cat /run/secrets/db-root-pass) \
	      --authenticationDatabase admin \
	      --ssl \
	      --sslCAFile /etc/ssl/certs/flags/root.crt