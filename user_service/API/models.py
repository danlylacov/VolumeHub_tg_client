from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Subscription(models.Model):
    telegram_id = models.IntegerField(unique=True)
    telegram_username = models.CharField(max_length=255)
    subscription = models.BooleanField(default=False)
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if self.end_date <= timezone.now():
            self.is_active = False
        super().save(*args, **kwargs)
