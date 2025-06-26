from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.subscribes.models import Subscribe
from apps.users.models import User


class Command(BaseCommand):
    help = "만료일 지난 구독은 is_active=False로 일괄 처리"

    def handle(self, *args, **options):
        now = timezone.now()
        expired_subs = Subscribe.objects.filter(is_active=True, expires_at__lt=now)
        user_ids = list(expired_subs.values_list("user_id", flat=True))
        expired_count = expired_subs.update(is_active=False)
        # 만료된 유저의 is_paid_user도 False로 동기화
        User.objects.filter(id__in=user_ids).update(is_paid_user=False)
        self.stdout.write(f"Expired {expired_count} subscriptions.")
