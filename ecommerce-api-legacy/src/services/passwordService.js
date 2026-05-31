'use strict';
const bcrypt = require('bcryptjs');

// Real password hashing — replaces the homegrown insecure `badCrypto`.
const passwordService = {
  hash: (plain) => bcrypt.hashSync(plain, 10),
  verify: (plain, hash) => bcrypt.compareSync(plain, hash),
};

module.exports = { passwordService };
