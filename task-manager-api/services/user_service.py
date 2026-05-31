"""User business logic — extracted out of the route handlers."""
from database import db
from models.user import User
from models.task import Task
from middlewares.error_handler import AppError
from shared.serializers import task_brief
from validators import user_validator as v


class UserService:
    def list(self):
        result = []
        for u in User.query.all():
            data = u.to_dict()
            data['task_count'] = len(u.tasks)
            result.append(data)
        return result

    def get(self, user_id):
        user = User.query.get(user_id)
        if not user:
            raise AppError('Usuário não encontrado', 404)
        data = user.to_dict()
        data['tasks'] = [t.to_dict() for t in Task.query.filter_by(user_id=user_id).all()]
        return data

    def create(self, data):
        if not data:
            raise AppError('Dados inválidos', 400)
        name = data.get('name')
        if not name:
            raise AppError('Nome é obrigatório', 400)
        email = v.validate_email(data.get('email'))
        password = v.validate_password(data.get('password'))
        role = v.validate_role(data.get('role', 'user'))

        if User.query.filter_by(email=email).first():
            raise AppError('Email já cadastrado', 409)

        user = User()
        user.name = name
        user.email = email
        user.set_password(password)
        user.role = role
        db.session.add(user)
        db.session.commit()
        return user.to_dict()

    def update(self, user_id, data):
        user = User.query.get(user_id)
        if not user:
            raise AppError('Usuário não encontrado', 404)
        if not data:
            raise AppError('Dados inválidos', 400)

        if 'name' in data:
            user.name = data['name']
        if 'email' in data:
            email = v.validate_email(data['email'])
            existing = User.query.filter_by(email=email).first()
            if existing and existing.id != user_id:
                raise AppError('Email já cadastrado', 409)
            user.email = email
        if 'password' in data:
            user.set_password(v.validate_password(data['password']))
        if 'role' in data:
            user.role = v.validate_role(data['role'])
        if 'active' in data:
            user.active = data['active']

        db.session.commit()
        return user.to_dict()

    def delete(self, user_id):
        user = User.query.get(user_id)
        if not user:
            raise AppError('Usuário não encontrado', 404)
        for t in Task.query.filter_by(user_id=user_id).all():
            db.session.delete(t)
        db.session.delete(user)
        db.session.commit()

    def user_tasks(self, user_id):
        user = User.query.get(user_id)
        if not user:
            raise AppError('Usuário não encontrado', 404)
        return [task_brief(t) for t in Task.query.filter_by(user_id=user_id).all()]

    def login(self, data):
        if not data:
            raise AppError('Dados inválidos', 400)
        email = data.get('email')
        password = data.get('password')
        if not email or not password:
            raise AppError('Email e senha são obrigatórios', 400)

        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(password):
            raise AppError('Credenciais inválidas', 401)
        if not user.active:
            raise AppError('Usuário inativo', 403)

        return {
            'message': 'Login realizado com sucesso',
            'user': user.to_dict(),
            'token': 'fake-jwt-token-' + str(user.id),
        }
