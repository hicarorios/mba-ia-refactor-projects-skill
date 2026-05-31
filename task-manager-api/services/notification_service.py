"""Email notifications. SMTP credentials come from config (env), never
hardcoded; operational messages go through the logger."""
import logging
import smtplib

from config.settings import settings
from shared.time import now_utc

logger = logging.getLogger('taskmanager.notifications')


class NotificationService:
    def __init__(self):
        self.notifications = []
        self.email_host = settings.SMTP_HOST
        self.email_port = settings.SMTP_PORT
        self.email_user = settings.SMTP_USER
        self.email_password = settings.SMTP_PASSWORD

    def send_email(self, to, subject, body):
        if not self.email_user or not self.email_password:
            logger.info("SMTP not configured; skipping email to %s (%s)", to, subject)
            return False
        try:
            server = smtplib.SMTP(self.email_host, self.email_port)
            server.starttls()
            server.login(self.email_user, self.email_password)
            server.sendmail(self.email_user, to, f"Subject: {subject}\n\n{body}")
            server.quit()
            logger.info("Email enviado para %s", to)
            return True
        except Exception as exc:
            logger.error("Erro ao enviar email: %s", exc)
            return False

    def notify_task_assigned(self, user, task):
        subject = f"Nova task atribuída: {task.title}"
        body = (f"Olá {user.name},\n\nA task '{task.title}' foi atribuída a você.\n\n"
                f"Prioridade: {task.priority}\nStatus: {task.status}")
        self.send_email(user.email, subject, body)
        self.notifications.append({
            'type': 'task_assigned',
            'user_id': user.id,
            'task_id': task.id,
            'timestamp': now_utc(),
        })

    def notify_task_overdue(self, user, task):
        subject = f"Task atrasada: {task.title}"
        body = (f"Olá {user.name},\n\nA task '{task.title}' está atrasada!\n\n"
                f"Data limite: {task.due_date}")
        self.send_email(user.email, subject, body)

    def get_notifications(self, user_id):
        return [n for n in self.notifications if n['user_id'] == user_id]
