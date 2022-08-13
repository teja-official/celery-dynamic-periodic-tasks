from celery import shared_task
from .models import UserPlan

@shared_task
def notify_on_planover(user=None, plan=None):
    userplan = UserPlan.objects.get(user__username=user, plan__id=plan)
    userplan.task.crontab.delete()
    print(f"Notifying user {user}")
    print(f"Dear {user}. Your plan({userplan.plan.name}) is expired. Please recharge now to avoid interruptions")

