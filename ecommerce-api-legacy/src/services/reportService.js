'use strict';

class ReportService {
  constructor(reportRepo) {
    this.reportRepo = reportRepo;
  }

  async financialReport() {
    const rows = await this.reportRepo.financialRows();
    const byCourse = new Map();

    for (const row of rows) {
      if (!byCourse.has(row.course_id)) {
        byCourse.set(row.course_id, { course: row.course_title, revenue: 0, students: [] });
      }
      const data = byCourse.get(row.course_id);
      // A null enrollment_id means the course has no enrollments (LEFT JOIN).
      if (row.enrollment_id == null) continue;
      if (row.payment_status === 'PAID') {
        data.revenue += row.payment_amount;
      }
      data.students.push({
        student: row.student_name || 'Unknown',
        paid: row.payment_amount != null ? row.payment_amount : 0,
      });
    }

    return Array.from(byCourse.values());
  }
}

module.exports = { ReportService };
