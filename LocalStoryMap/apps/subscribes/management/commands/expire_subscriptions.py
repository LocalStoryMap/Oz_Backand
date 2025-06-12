from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.subscribes.models import Subscribe


class Command(BaseCommand):
    help = "만료일 지난 구독은 is_active=False로 일괄 처리"

    def handle(self, *args, **options):
        now = timezone.now()
        expired_count = Subscribe.objects.filter(
            is_active=True, expires_at__lt=now
        ).update(is_active=False)
        self.stdout.write(f"Expired {expired_count} subscriptions.")
