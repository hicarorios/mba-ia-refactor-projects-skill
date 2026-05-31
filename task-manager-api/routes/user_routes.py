"""User routing only — delegates to the user controller."""
from flask import Blueprint

from controllers.user_controller import user_controller

user_bp = Blueprint('users', __name__)

user_bp.add_url_rule('/users', 'get_users', user_controller.list, methods=['GET'])
user_bp.add_url_rule('/users/<int:user_id>', 'get_user', user_controller.get, methods=['GET'])
user_bp.add_url_rule('/users', 'create_user', user_controller.create, methods=['POST'])
user_bp.add_url_rule('/users/<int:user_id>', 'update_user', user_controller.update, methods=['PUT'])
user_bp.add_url_rule('/users/<int:user_id>', 'delete_user', user_controller.delete, methods=['DELETE'])
user_bp.add_url_rule('/users/<int:user_id>/tasks', 'get_user_tasks', user_controller.tasks, methods=['GET'])
user_bp.add_url_rule('/login', 'login', user_controller.login, methods=['POST'])
