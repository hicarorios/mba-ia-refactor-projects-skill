from flask import request, jsonify

from services.user_service import UserService

service = UserService()


class UserController:
    def list(self):
        return jsonify(service.list()), 200

    def get(self, user_id):
        return jsonify(service.get(user_id)), 200

    def create(self):
        return jsonify(service.create(request.get_json(silent=True))), 201

    def update(self, user_id):
        return jsonify(service.update(user_id, request.get_json(silent=True))), 200

    def delete(self, user_id):
        service.delete(user_id)
        return jsonify({'message': 'Usuário deletado com sucesso'}), 200

    def tasks(self, user_id):
        return jsonify(service.user_tasks(user_id)), 200

    def login(self):
        return jsonify(service.login(request.get_json(silent=True))), 200


user_controller = UserController()
