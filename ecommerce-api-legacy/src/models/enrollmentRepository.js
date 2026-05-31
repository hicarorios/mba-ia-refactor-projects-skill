'use strict';

class EnrollmentRepository {
  constructor(db) {
    this.db = db;
  }

  async create(userId, courseId) {
    const { lastID } = await this.db.run(
      'INSERT INTO enrollments (user_id, course_id) VALUES (?, ?)',
      [userId, courseId]
    );
    return lastID;
  }

  deleteByUser(userId) {
    return this.db.run('DELETE FROM enrollments WHERE user_id = ?', [userId]);
  }

  idsByUser(userId) {
    return this.db.all('SELECT id FROM enrollments WHERE user_id = ?', [userId]);
  }
}

module.exports = { EnrollmentRepository };
