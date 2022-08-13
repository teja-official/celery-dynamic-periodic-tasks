from datetime import timedelta
import json
from django.utils import timezone
from django.db import models
from django_celery_beat.models import CrontabSchedule, PeriodicTask
from django.contrib.auth.models import User

class Plan(models.Model):
    name = models.CharField(verbose_name='Plan name', max_length=30)
    amount = models.DecimalField(max_digits=7, decimal_places=2)
    period = models.PositiveSmallIntegerField(help_text='days')
    def __str__(self):
        return f"{self.name} for {self.period} days"

class UserPlan(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
    expires_at = models.DateTimeField(blank=True, null=True)
    task = models.OneToOneField(PeriodicTask, on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} :: {self.plan.name}"

    def scheduler(self, expires_at):
        schedule, _ = CrontabSchedule.objects.get_or_create(
            minute=expires_at.minute,
            hour=expires_at.hour,
            day_of_week=expires_at.isoweekday(),
            day_of_month=expires_at.day,
            month_of_year=expires_at.month,
        )
        return schedule

    def save(self):
        self.task = PeriodicTask.objects.create(
            crontab = self.scheduler(self.expires_at),
            name = f'Notifying plan over. Plan-{self.plan.name}',
            task = 'app.tasks.notify_on_planover',
            kwargs = json.dumps({'user': self.user.username, 'plan': self.plan.pk}),
            one_off = True  # We need the task to be executed only once
        )
        super().save()
