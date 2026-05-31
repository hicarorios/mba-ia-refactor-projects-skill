"""Report & category routing only — delegates to the controllers."""
from flask import Blueprint

from controllers.report_controller import report_controller
from controllers.category_controller import category_controller

report_bp = Blueprint('reports', __name__)

report_bp.add_url_rule('/reports/summary', 'summary_report', report_controller.summary, methods=['GET'])
report_bp.add_url_rule('/reports/user/<int:user_id>', 'user_report', report_controller.user_report, methods=['GET'])

report_bp.add_url_rule('/categories', 'get_categories', category_controller.list, methods=['GET'])
report_bp.add_url_rule('/categories', 'create_category', category_controller.create, methods=['POST'])
report_bp.add_url_rule('/categories/<int:cat_id>', 'update_category', category_controller.update, methods=['PUT'])
report_bp.add_url_rule('/categories/<int:cat_id>', 'delete_category', category_controller.delete, methods=['DELETE'])
