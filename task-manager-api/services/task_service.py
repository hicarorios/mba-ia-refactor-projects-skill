"""Task business logic — extracted out of the route handlers."""
from database import db
from models.task import Task
from models.user import User
from models.category import Category
from middlewares.error_handler import AppError
from shared.serializers import task_full
from validators import task_validator as v


class TaskService:
    def list(self):
        return [task_full(t) for t in Task.query.all()]

    def get(self, task_id):
        task = Task.query.get(task_id)
        if not task:
            raise AppError('Task não encontrada', 404)
        data = task.to_dict()
        data['overdue'] = task.is_overdue()
        return data

    def _check_refs(self, user_id, category_id):
        if user_id and not User.query.get(user_id):
            raise AppError('Usuário não encontrado', 404)
        if category_id and not Category.query.get(category_id):
            raise AppError('Categoria não encontrada', 404)

    def create(self, data):
        if not data:
            raise AppError('Dados inválidos', 400)

        title = v.validate_title(data.get('title'))
        status = v.validate_status(data.get('status', 'pending'))
        priority = v.validate_priority(data.get('priority', 3))
        user_id = data.get('user_id')
        category_id = data.get('category_id')
        self._check_refs(user_id, category_id)

        task = Task()
        task.title = title
        task.description = data.get('description', '')
        task.status = status
        task.priority = priority
        task.user_id = user_id
        task.category_id = category_id
        task.due_date = v.parse_due_date(data.get('due_date'))
        tags = v.normalize_tags(data.get('tags'))
        if tags is not None:
            task.tags = tags

        db.session.add(task)
        db.session.commit()
        return task.to_dict()

    def update(self, task_id, data):
        task = Task.query.get(task_id)
        if not task:
            raise AppError('Task não encontrada', 404)
        if not data:
            raise AppError('Dados inválidos', 400)

        if 'title' in data:
            task.title = v.validate_title(data['title'])
        if 'description' in data:
            task.description = data['description']
        if 'status' in data:
            task.status = v.validate_status(data['status'])
        if 'priority' in data:
            task.priority = v.validate_priority(data['priority'])
        if 'user_id' in data:
            self._check_refs(data['user_id'], None)
            task.user_id = data['user_id']
        if 'category_id' in data:
            self._check_refs(None, data['category_id'])
            task.category_id = data['category_id']
        if 'due_date' in data:
            task.due_date = v.parse_due_date(data['due_date'])
        if 'tags' in data:
            task.tags = v.normalize_tags(data['tags'])

        db.session.commit()
        return task.to_dict()

    def delete(self, task_id):
        task = Task.query.get(task_id)
        if not task:
            raise AppError('Task não encontrada', 404)
        db.session.delete(task)
        db.session.commit()

    def search(self, query='', status='', priority='', user_id=''):
        q = Task.query
        if query:
            q = q.filter(db.or_(Task.title.like(f'%{query}%'),
                                Task.description.like(f'%{query}%')))
        if status:
            q = q.filter(Task.status == status)
        if priority:
            q = q.filter(Task.priority == int(priority))
        if user_id:
            q = q.filter(Task.user_id == int(user_id))
        return [t.to_dict() for t in q.all()]

    def stats(self):
        tasks = Task.query.all()
        total = len(tasks)
        by_status = {s: 0 for s in ('pending', 'in_progress', 'done', 'cancelled')}
        overdue = 0
        for t in tasks:
            if t.status in by_status:
                by_status[t.status] += 1
            if t.is_overdue():
                overdue += 1
        return {
            'total': total,
            **by_status,
            'overdue': overdue,
            'completion_rate': round((by_status['done'] / total) * 100, 2) if total else 0,
        }
