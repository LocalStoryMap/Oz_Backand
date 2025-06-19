from rest_framework import serializers


class SummarizeRequestSerializer(serializers.Serializer):
    """
    요약 요청 시: marker_id 로 DB lookup 하거나, raw_text 직접 넣어주는 방식 지원
    """

    marker_id = serializers.IntegerField(required=False, help_text="DB에 저장된 지역 ID")
    raw_text = serializers.CharField(required=False, help_text="직접 전달할 긴 텍스트")

    def validate(self, attrs):
        marker_id = attrs.get("marker_id")
        raw_text = attrs.get("raw_text")

        if not marker_id and not raw_text:
            raise serializers.ValidationError(
                "marker_id 또는 raw_text 중 최소 하나는 입력해야 합니다."
            )
        return attrs


class ChatRequestSerializer(serializers.Serializer):
    """
    챗봇 대화 요청 시: messages 목록을 그대로 전달
    """

    messages = serializers.ListField(
        child=serializers.DictField(child=serializers.CharField()),
        help_text="Clova Chat API 형식에 맞춰진 메시지 리스트",
    )
