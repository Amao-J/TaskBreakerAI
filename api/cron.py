# cron.py
from django_cron import CronJobBase, Schedule
from django.utils.timezone import now
from .models import Goals
from django.core.mail import send_mail

class NotifyOverdueGoalsJob(CronJobBase):
    RUN_EVERY_MINS = 60  

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'api.notify_overdue_goals' 

    def do(self):
        overdue_goals = Goals.objects.filter(completed=False, due_date__lt=now())
        for goal in overdue_goals:
            send_mail(
                'Overdue Goal Notification',
                f'Your goal "{goal.description}" is overdue.',
                'admin@yourdomain.com',
                [goal.user.email],
                fail_silently=False,
            )
