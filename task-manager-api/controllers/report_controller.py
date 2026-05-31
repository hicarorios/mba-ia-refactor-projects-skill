from flask import jsonify

from services.report_service import ReportService

service = ReportService()


class ReportController:
    def summary(self):
        return jsonify(service.summary()), 200

    def user_report(self, user_id):
        return jsonify(service.user_report(user_id)), 200


report_controller = ReportController()
