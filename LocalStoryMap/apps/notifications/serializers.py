from rest_framework import serializers

from .models import NotificationSetting


class NotificationSettingSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True, label="ID")
    type = serializers.CharField(label="알림 유형")
    enabled = serializers.BooleanField(label="활성화 여부")
    created_at = serializers.DateTimeField(read_only=True, label="생성일")
    updated_at = serializers.DateTimeField(read_only=True, label="수정일")

    class Meta:
        model = NotificationSetting
        fields = ["id", "type", "enabled", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]
