from flask import request, jsonify

from services.task_service import TaskService

service = TaskService()


class TaskController:
    def list(self):
        return jsonify(service.list()), 200

    def get(self, task_id):
        return jsonify(service.get(task_id)), 200

    def create(self):
        return jsonify(service.create(request.get_json(silent=True))), 201

    def update(self, task_id):
        return jsonify(service.update(task_id, request.get_json(silent=True))), 200

    def delete(self, task_id):
        service.delete(task_id)
        return jsonify({'message': 'Task deletada com sucesso'}), 200

    def search(self):
        return jsonify(service.search(
            query=request.args.get('q', ''),
            status=request.args.get('status', ''),
            priority=request.args.get('priority', ''),
            user_id=request.args.get('user_id', ''),
        )), 200

    def stats(self):
        return jsonify(service.stats()), 200


task_controller = TaskController()
