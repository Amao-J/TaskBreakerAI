
from celery import shared_task
from django.utils.timezone import now
from .models import Goals
from django.core.mail import send_mail
from .models import Dashboard
from .notifications import send_push_notification

@shared_task
def send_weekly_reports():
    """Send weekly reports via email and push notifications."""
    dashboards = Dashboard.objects.all()
    
    for dashboard in dashboards:
        report = dashboard.generate_report(period='week')
        user = dashboard.user

        # Email Report
        subject = "📊 Your Weekly Productivity Report"
        message = f"""
        Hello {user.first_name or 'User'},

        ✅ Goals Completed: {report['completed_goals']} / {report['total_goals']}
        ✅ Task Completion Rate: {report['task_completion_rate']:.2f}%

        Keep up the good work! 🎯
        """
        send_mail(subject, message, 'no-reply@yourapp.com', [user.email])

        # Push Notification
        if user.fcm_token:
            send_push_notification(
                user.fcm_token,
                "Weekly Report 📊",
                f"{report['completed_goals']} goals completed! Keep going! 🚀"
            )

@shared_task
def send_monthly_reports():
    """Send monthly reports via email and push notifications."""
    dashboards = Dashboard.objects.all()
    
    for dashboard in dashboards:
        report = dashboard.generate_report(period='month')
        user = dashboard.user

        # Email Report
        subject = "📈 Your Monthly Productivity Report"
        message = f"""
        Hey {user.first_name or 'User'},

        🎯 Goals Completed: {report['completed_goals']} / {report['total_goals']}
        📌 Task Completion Rate: {report['task_completion_rate']:.2f}%

        Keep pushing towards your goals! 🚀
        """
        send_mail(subject, message, 'no-reply@yourapp.com', [user.email])

        # Push Notification
        if user.fcm_token:
            send_push_notification(
                user.fcm_token,
                "Monthly Report 📈",
                f"{report['completed_goals']} goals completed! Keep achieving! 🏆"
            )

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

