from flask import request, jsonify

from services.category_service import CategoryService

service = CategoryService()


class CategoryController:
    def list(self):
        return jsonify(service.list()), 200

    def create(self):
        return jsonify(service.create(request.get_json(silent=True))), 201

    def update(self, cat_id):
        return jsonify(service.update(cat_id, request.get_json(silent=True))), 200

    def delete(self, cat_id):
        service.delete(cat_id)
        return jsonify({'message': 'Categoria deletada'}), 200


category_controller = CategoryController()
