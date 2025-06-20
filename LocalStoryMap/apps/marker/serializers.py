from rest_framework import serializers

from .models import Marker


class MarkerSerializer(serializers.ModelSerializer):
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = Marker
        fields = [
            "id",
            "marker_name",
            "adress",
            "description",
            "image",
            "latitude",
            "longitude",
            "created_at",
            "updated_at",
            "coordinate",  # @property 필드
            "layer",
            "like_count",
            "is_liked",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
            "coordinate",
            "like_count",
            "is_liked",
        ]

    def validate_latitude(self, value):
        if not (-90 <= value <= 90):
            raise serializers.ValidationError("위도는 -90과 90 사이여야 합니다.")
        return value

    def validate_longitude(self, value):
        if not (-180 <= value <= 180):
            raise serializers.ValidationError("경도는 -180과 180 사이여야 합니다.")
        return value

    def get_is_liked(self, obj):
        user = self.context["request"].user
        if user.is_authenticated:
            return obj.likes.filter(user=user, is_liked=True).exists()
        return False


class MarkerListFilterSerializer(serializers.Serializer):
    # 마커 목록 조회의 쿼리 파라미터 유효성 검사를 위한 시리얼라이저.
    story_id = serializers.IntegerField(required=False)
    search_term = serializers.CharField(required=False, max_length=100)
    layer = serializers.CharField(required=False, max_length=20)
    latitude = serializers.FloatField(required=False)
    longitude = serializers.FloatField(required=False)
    radius = serializers.FloatField(
        required=False, default=10.0, min_value=0.1, max_value=50.0
    )

    def validate(self, attrs):
        # 위치 기반 검색 시 위도/경도가 모두 있어야 함을 검증합니다.
        lat = attrs.get("latitude")
        lng = attrs.get("longitude")

        if (lat is not None and lng is None) or (lat is None and lng is not None):
            raise serializers.ValidationError(
                "위치 기반 검색을 위해서는 latitude와 longitude를 모두 제공해야 합니다."
            )

        return attrs

    def validate_layer(self, value):
        valid_layers = ["tour", "food", "infra"]
        if value and value not in valid_layers:
            raise serializers.ValidationError(f"유효하지 않은 layer 값입니다. ({valid_layers})")
        return value
