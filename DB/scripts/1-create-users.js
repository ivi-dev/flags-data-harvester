const fs = require('fs');

const rootUser = getUserData("root"),
      backendUser = getUserData("backend"),
      dataHarvesterUser = getUserData("data-harvester"),
      adminDB = "admin",
      flagsDB = "flags",
      cluster = Mongo();

db = cluster.getDB("admin");

// db.auth(rootUser.user, rootUser.pwd);
     
// Create the "ROOT" user
tryCreateUser(db, rootUser, [ { role: "root", db: adminDB } ]);

// db.createUser({
//     ...rootUser,
//     roles: [
//         { role: "root", db: adminDB }
//     ],
// });

db = db.getSiblingDB(flagsDB);

// Create the "DATA-HARVESTER" user
tryCreateUser(db, dataHarvesterUser, [ { role: "readWrite", db: flagsDB } ]);

// db.createUser({
//     ...dataHarvesterUser,
//     roles: [
//         { role: "readWrite", db: flagsDB }
//     ],
// });

// Create the "BACKEND" user
tryCreateUser(db, backendUser, [ { role: "read", db: flagsDB } ]);

// db.createUser({
//     ...backendUser,
//     roles: [
//         { role: "read", db: flagsDB }
//     ],
// });

function getUserData(type) {
    const userTypes = ["root", "backend", "data-harvester"];
    if (!userTypes.includes(type))
        throw new Error(
            `Invalid user type provided. Options are: ${userTypes.join(", ")}`
        );
    const opts = { encoding: "utf8" },
          username = fs.readFileSync(`/run/secrets/db-${type}-user`, opts),
          password = fs.readFileSync(`/run/secrets/db-${type}-pass`, opts);
    return {
        user: username.trim(),
        pwd: password.trim(),
    };
}

function userExists(db, username) {
    const users = db.getUsers();
    return users.some(user => user.user === username);
}

function tryCreateUser(db, userData, roles) {
    if (userExists(db, userData.user)) {
        print(`User ${userData.user} already exists. Skipping creation.`);
        return;
    }
    db.createUser({
        ...userData,
        roles: roles
    });
}