"""Task routing only — delegates to the task controller."""
from flask import Blueprint

from controllers.task_controller import task_controller

task_bp = Blueprint('tasks', __name__)

task_bp.add_url_rule('/tasks', 'get_tasks', task_controller.list, methods=['GET'])
task_bp.add_url_rule('/tasks/search', 'search_tasks', task_controller.search, methods=['GET'])
task_bp.add_url_rule('/tasks/stats', 'task_stats', task_controller.stats, methods=['GET'])
task_bp.add_url_rule('/tasks/<int:task_id>', 'get_task', task_controller.get, methods=['GET'])
task_bp.add_url_rule('/tasks', 'create_task', task_controller.create, methods=['POST'])
task_bp.add_url_rule('/tasks/<int:task_id>', 'update_task', task_controller.update, methods=['PUT'])
task_bp.add_url_rule('/tasks/<int:task_id>', 'delete_task', task_controller.delete, methods=['DELETE'])
