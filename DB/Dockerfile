FROM ubuntu:noble

ENV MONGO_VERSION="8.0" \
    SYSTEM_DB_USER="mongodb" \
    SYSTEM_DB_GROUP="mongodb" \
    DUMPS_PATH="/var/mongo/dumps" \
    SSL_PATH="/etc/ssl/private" \ 
    DATA_PATH="/data/db" \
    LOG_PATH="/var/log/mongodb/mongod.log" \
    PID_PATH="/var/run/mongodb/mongod.pid" \
    CONFIG_PATH="/etc/mongod.conf"
    

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
RUN mkdir -p $DUMPS_PATH
RUN chown $SYSTEM_DB_USER $DUMPS_PATH
RUN chmod -R 704 $DUMPS_PATH
RUN chmod o+rx $SSL_PATH
COPY mongod.conf $CONFIG_PATH
RUN chown $SYSTEM_DB_USER $CONFIG_PATH && \
    chmod 700 $CONFIG_PATH


# ========================================
#       Initialize and start MongoDB
# ========================================

COPY scripts/setup-db.sh /root
RUN mkdir -p /docker-entrypoint-initdb.d
COPY scripts/dump-db.sh \
     scripts/restore-db.sh \
     /docker-entrypoint-initdb.d/
RUN /root/setup-db.sh

USER $SYSTEM_DB_USER

ENTRYPOINT [ "mongod" ]
CMD [ "--config", "/etc/mongod.conf" ]