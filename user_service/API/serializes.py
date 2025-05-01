from django.contrib.postgres import serializers

from .models import Subscription
from django.contrib.auth.models import User
from django.utils import timezone


class SubscriptionSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = Subscription
        fields = ['id', 'user', 'subscription_type', 'start_date', 'end_date', 'is_active']
        read_only_fields = ['start_date', 'is_active']

    def validate_end_date(self, value):
        if value <= timezone.now():
            raise serializers.ValidationError("Дата окончания подписки должна быть в будущем")
        return value
