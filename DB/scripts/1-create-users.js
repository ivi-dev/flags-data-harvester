const fs = require('fs');

const rootUser = getUserData("root"),
      backendUser = getUserData("backend"),
      dataHarvesterUser = getUserData("data-harvester"),
      flagsDB = "flags",
      cluster = Mongo();

db = cluster.getDB("admin");

db.auth(rootUser.user, rootUser.pwd);
     
db = db.getSiblingDB(flagsDB);

// Create the "DATA-HARVESTER" user
db.createUser({
    ...dataHarvesterUser,
    roles: [
        { role: "readWrite", db: flagsDB }
    ],
});

// Create the "BACKEND" user
db.createUser({
    ...backendUser,
    roles: [
        { role: "read", db: flagsDB }
    ],
});

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