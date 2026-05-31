"""Reporting business logic — extracted out of the route handlers.
Overdue detection reuses Task.is_overdue() instead of re-implementing it."""
from datetime import timedelta

from models.task import Task
from models.user import User
from models.category import Category
from middlewares.error_handler import AppError
from shared.time import now_utc

RECENT_WINDOW_DAYS = 7
HIGH_PRIORITY_THRESHOLD = 2


class ReportService:
    def summary(self):
        all_tasks = Task.query.all()

        by_status = {s: 0 for s in ('pending', 'in_progress', 'done', 'cancelled')}
        by_priority = {p: 0 for p in range(1, 6)}
        overdue_list = []
        now = now_utc()
        for t in all_tasks:
            if t.status in by_status:
                by_status[t.status] += 1
            if t.priority in by_priority:
                by_priority[t.priority] += 1
            if t.is_overdue():
                overdue_list.append({
                    'id': t.id,
                    'title': t.title,
                    'due_date': str(t.due_date),
                    'days_overdue': (now - t.due_date).days,
                })

        window_start = now - timedelta(days=RECENT_WINDOW_DAYS)
        recent_tasks = Task.query.filter(Task.created_at >= window_start).count()
        recent_done = Task.query.filter(
            Task.status == 'done', Task.updated_at >= window_start
        ).count()

        user_stats = []
        for u in User.query.all():
            user_tasks = Task.query.filter_by(user_id=u.id).all()
            total = len(user_tasks)
            completed = sum(1 for t in user_tasks if t.status == 'done')
            user_stats.append({
                'user_id': u.id,
                'user_name': u.name,
                'total_tasks': total,
                'completed_tasks': completed,
                'completion_rate': round((completed / total) * 100, 2) if total else 0,
            })

        return {
            'generated_at': str(now),
            'overview': {
                'total_tasks': len(all_tasks),
                'total_users': User.query.count(),
                'total_categories': Category.query.count(),
            },
            'tasks_by_status': by_status,
            'tasks_by_priority': {
                'critical': by_priority[1],
                'high': by_priority[2],
                'medium': by_priority[3],
                'low': by_priority[4],
                'minimal': by_priority[5],
            },
            'overdue': {'count': len(overdue_list), 'tasks': overdue_list},
            'recent_activity': {
                'tasks_created_last_7_days': recent_tasks,
                'tasks_completed_last_7_days': recent_done,
            },
            'user_productivity': user_stats,
        }

    def user_report(self, user_id):
        user = User.query.get(user_id)
        if not user:
            raise AppError('Usuário não encontrado', 404)

        tasks = Task.query.filter_by(user_id=user_id).all()
        total = len(tasks)
        counts = {s: 0 for s in ('done', 'pending', 'in_progress', 'cancelled')}
        overdue = 0
        high_priority = 0
        for t in tasks:
            if t.status in counts:
                counts[t.status] += 1
            if t.priority <= HIGH_PRIORITY_THRESHOLD:
                high_priority += 1
            if t.is_overdue():
                overdue += 1

        return {
            'user': {'id': user.id, 'name': user.name, 'email': user.email},
            'statistics': {
                'total_tasks': total,
                'done': counts['done'],
                'pending': counts['pending'],
                'in_progress': counts['in_progress'],
                'cancelled': counts['cancelled'],
                'overdue': overdue,
                'high_priority': high_priority,
                'completion_rate': round((counts['done'] / total) * 100, 2) if total else 0,
            },
        }
