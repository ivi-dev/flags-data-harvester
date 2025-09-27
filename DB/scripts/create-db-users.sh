#!/bin/bash

# ========================================
# Create initial database users
# ========================================

mongosh --host localhost \
        --eval "use admin" \
        --eval "const user = '$(cat /run/secrets/db-root-user)', \
                      pwd = '$(cat /run/secrets/db-root-pass)'; \
                const users = db.getUsers().users; \
                if (!users.some(u => u.user === user)) { \
                    db.createUser({ \
                        user, \
                        pwd, \
                        roles: [ { role: 'root', db: 'admin' } ] \
                    }); \
                }" \
        --eval "use flags" \
        --eval "const user = '$(cat /run/secrets/db-data-harvester-user)', \
                      pwd = '$(cat /run/secrets/db-data-harvester-pass)'; \
                const users = db.getUsers().users; \
                if (!users.some(u => u.user === user)) { \
                    db.createUser({ \
                        user, \
                        pwd, \
                        roles: [ { role: 'readWrite', db: 'flags' } ] \
                    }); \
                }" \
        --eval "const user = '$(cat /run/secrets/db-backend-user)', \
                      pwd = '$(cat /run/secrets/db-backend-pass)'; \
                const users = db.getUsers().users; \
                if (!users.some(u => u.user === user)) { \
                    db.createUser({ \
                        user, \
                        pwd, \
                        roles: [ { role: 'read', db: 'flags' } ] \
                    }); \
                }"