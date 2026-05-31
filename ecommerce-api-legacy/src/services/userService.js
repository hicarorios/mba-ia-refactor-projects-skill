'use strict';

// Deleting a user now cascades to its enrollments and payments, within a
// transaction — no more orphaned rows.
class UserService {
  constructor({ db, userRepo, enrollmentRepo, paymentRepo }) {
    this.db = db;
    this.userRepo = userRepo;
    this.enrollmentRepo = enrollmentRepo;
    this.paymentRepo = paymentRepo;
  }

  async deleteUser(id) {
    const enrollments = await this.enrollmentRepo.idsByUser(id);
    const enrollmentIds = enrollments.map((e) => e.id);

    await this.db.run('BEGIN');
    try {
      await this.paymentRepo.deleteByEnrollmentIds(enrollmentIds);
      await this.enrollmentRepo.deleteByUser(id);
      await this.userRepo.delete(id);
      await this.db.run('COMMIT');
    } catch (err) {
      await this.db.run('ROLLBACK');
      throw err;
    }
  }
}

module.exports = { UserService };
