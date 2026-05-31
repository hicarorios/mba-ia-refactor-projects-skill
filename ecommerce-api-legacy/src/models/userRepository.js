'use strict';

class UserRepository {
  constructor(db) {
    this.db = db;
  }

  findByEmail(email) {
    return this.db.get('SELECT * FROM users WHERE email = ?', [email]);
  }

  async create(name, email, passHash) {
    const { lastID } = await this.db.run(
      'INSERT INTO users (name, email, pass) VALUES (?, ?, ?)',
      [name, email, passHash]
    );
    return lastID;
  }

  delete(id) {
    return this.db.run('DELETE FROM users WHERE id = ?', [id]);
  }
}

module.exports = { UserRepository };
