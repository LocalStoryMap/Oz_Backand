from rest_framework import serializers

from .models import PaymentHistory


class PaymentHistorySerializer(serializers.ModelSerializer):
    """결제 이력 시리얼라이저"""

    user_email = serializers.EmailField(source="user.email", read_only=True)

    class Meta:
        model = PaymentHistory
        fields = [
            "id",
            "user",
            "user_email",
            "imp_uid",
            "merchant_uid",
            "amount",
            "status",
            "payment_method",
            "card_name",
            "card_number",
            "paid_at",
            "receipt_url",
            "created_at",
            "updated_at",
            "is_delete",
        ]
        read_only_fields = [
            "id",
            "user",
            "user_email",
            "imp_uid",
            "merchant_uid",
            "amount",
            "status",
            "payment_method",
            "card_name",
            "card_number",
            "paid_at",
            "receipt_url",
            "created_at",
            "updated_at",
            "is_delete",
        ] 