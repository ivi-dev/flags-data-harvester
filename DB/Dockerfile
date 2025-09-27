FROM ubuntu:noble

ENV MONGO_VERSION="8.0" \
    SYSTEM_DB_USER="mongodb" \
    SYSTEM_DB_GROUP="mongodb" \
    SSL_PATH="/etc/ssl/private" \ 
    ROOT_CA_PATH="/etc/ssl/certs/flags/root.crt" \ 
    SYSTEM_CA_CERTS_PATH="/usr/local/share/ca-certificates" \ 
    DATA_PATH="/data/db" \
    LOG_PATH="/var/log/mongodb/mongod.log" \
    PID_PATH="/var/run/mongodb/mongod.pid" \
    CONFIG_PATH="/etc/mongod.conf" \
    NO_TLS_NO_AUTH_CONFIG_PATH="/etc/mongod-no-tls-no-auth.conf" \
    MONGO_SCRIPTS_PATH="/etc/mongo" \
    DUMP_BASE_DIR="/var/mongo/dumps" \
    USER_NAME_FILE="/run/secrets/db-root-user" \
    USER_PASS_FILE="/run/secrets/db-root-pass" \
    AUTH_DB="admin" \
    SSL_CA_FILE="/etc/ssl/certs/flags/root.crt" \
    GLIBC_TUNABLES="glibc.pthread.rseq=0" \
    MONGO_START_TIMEOUT=5
    

# ========================================
#             Install MongoDB
# ========================================

RUN apt-get clean && apt-get update && apt-get install -y gnupg curl
RUN curl -fsSL https://www.mongodb.org/static/pgp/server-$MONGO_VERSION.asc | \
    gpg -o /usr/share/keyrings/mongodb-server-$MONGO_VERSION.gpg --dearmor
RUN echo "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-$MONGO_VERSION.gpg ] \
          https://repo.mongodb.org/apt/ubuntu noble/mongodb-org/$MONGO_VERSION multiverse" | \
    tee /etc/apt/sources.list.d/mongodb-org-$MONGO_VERSION.list
RUN apt-get update && apt-get install -y mongodb-org
RUN chmod -R o+rx $SSL_PATH
COPY mongod.conf $CONFIG_PATH
COPY mongod-no-tls-no-auth.conf $NO_TLS_NO_AUTH_CONFIG_PATH
RUN chown $SYSTEM_DB_USER $CONFIG_PATH $NO_TLS_NO_AUTH_CONFIG_PATH && \
    chmod 700 $CONFIG_PATH $NO_TLS_NO_AUTH_CONFIG_PATH


# ========================================
#       Initialize and start MongoDB
# ========================================

COPY scripts/setup-db.sh /root
RUN /root/setup-db.sh
RUN mkdir $MONGO_SCRIPTS_PATH
COPY scripts/create-db-users.sh \
     scripts/dump-db.sh \
     scripts/restore-db.sh \
     $MONGO_SCRIPTS_PATH/
RUN chown -R $SYSTEM_DB_USER $MONGO_SCRIPTS_PATH && \
    chmod 700 -R $MONGO_SCRIPTS_PATH

WORKDIR $MONGO_SCRIPTS_PATH

RUN --mount=type=secret,id=db-root-user \
    --mount=type=secret,id=db-root-pass \ 
    --mount=type=secret,id=db-backend-user \ 
    --mount=type=secret,id=db-backend-pass \ 
    --mount=type=secret,id=db-data-harvester-user \ 
    --mount=type=secret,id=db-data-harvester-pass \ 
    mongod --fork --logpath $LOG_PATH --logappend --config $NO_TLS_NO_AUTH_CONFIG_PATH && \
    sleep $MONGO_START_TIMEOUT && \
    ./create-db-users.sh && \
    mongod --config $NO_TLS_NO_AUTH_CONFIG_PATH --shutdown
RUN chown -R $SYSTEM_DB_USER:$SYSTEM_DB_GROUP $DATA_PATH && \
    chmod -R 700 $DATA_PATH

USER $SYSTEM_DB_USER

ENTRYPOINT [ "mongod" ]
CMD [ "--config", "/etc/mongod.conf" ]