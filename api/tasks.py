
from celery import shared_task
from django.utils.timezone import now
from .models import Goals
from django.core.mail import send_mail

@shared_task
def notify_overdue_goals():
    overdue_goals = Goals.objects.filter(completed=False, due_date__lt=now())
    for goal in overdue_goals:
        send_mail(
            'Overdue Goal Notification',
            f'Your goal "{goal.description}" is overdue.',
            'admin@pina.com',
            [goal.user.email],
            fail_silently=False,
        )

