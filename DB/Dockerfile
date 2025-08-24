FROM mongo:8

COPY scripts/combine-cert-and-key.sh /root
COPY scripts/*.js /docker-entrypoint-initdb.d
COPY scripts/dump-db.sh /root
RUN mkdir -p /var/mongo/dumps
COPY mongod.conf /etc/mongod.conf
RUN chmod 755 /etc/ssl/private