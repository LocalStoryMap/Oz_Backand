# apps/route/serializers.py
from rest_framework import serializers

from apps.marker.serializers import MarkerSerializer

from .models import Route


class RouteSerializer(serializers.ModelSerializer):
    # 경로 모델의 기본 시리얼라이저
    user: serializers.StringRelatedField = (
        serializers.StringRelatedField()
    )  # 사용자 정보를 닉네임 등으로 간단히 표시
    marker_count = serializers.IntegerField(read_only=True)  # @property 필드

    class Meta:
        model = Route
        fields = [
            "id",
            "user",
            "name",
            "description",
            "created_at",
            "updated_at",
            "is_public",
            "marker_count",
            "like_count",
        ]
        read_only_fields = ["id", "user", "created_at", "updated_at", "marker_count", "like_count"]


class RouteCreateSerializer(serializers.ModelSerializer):
    # 경로 생성 시리얼라이저

    class Meta:
        model = Route
        fields = [
            "name",
            "description",
            "is_public",
        ]

    def validate_name(self, value):
        if len(value.strip()) < 2:
            raise serializers.ValidationError("경로명은 최소 2글자 이상이어야 합니다.")

        user = self.context["request"].user
        if Route.objects.filter(user=user, name=value).exists():
            raise serializers.ValidationError("이미 같은 이름의 경로를 사용하고 있습니다.")

        return value


class RouteUpdateSerializer(serializers.ModelSerializer):
    # 경로 수정을 위한 시리얼라이저

    class Meta:
        model = Route
        fields = [
            "name",
            "description",
            "is_public",
        ]

    def validate_name(self, value):
        if len(value.strip()) < 2:
            raise serializers.ValidationError("경로명은 최소 2글자 이상이어야 합니다.")

        user = self.context["request"].user
        instance = self.instance
        # exclude를 사용해 원래 이름을 제외하고 검사
        if Route.objects.filter(user=user, name=value).exclude(pk=instance.pk).exists():
            raise serializers.ValidationError("이미 같은 이름의 경로를 사용하고 있습니다.")

        return value


class OrderedMarkerSerializer(MarkerSerializer):
    # 경로에 포함된 마커를 위한 시리얼라이저 (순서 정보 추가)
    sequence = serializers.IntegerField()

    class Meta(MarkerSerializer.Meta):
        fields = MarkerSerializer.Meta.fields + ["sequence"]


class RouteWithOrderedMarkersSerializer(RouteSerializer):
    # 경로 상세 정보와 순서대로 정렬된 마커 목록을 포함하는 시리얼라이저
    markers = serializers.SerializerMethodField()

    class Meta(RouteSerializer.Meta):
        fields = RouteSerializer.Meta.fields + ["markers"]

    def get_markers(self, obj):
        # 순서대로 정렬된 마커 목록을 반환합니다
        ordered_route_markers = obj.route_markers.select_related("marker").order_by(
            "sequence"
        )

        # Marker에 sequence 정보를 추가
        markers_with_sequence = []
        for rm in ordered_route_markers:
            marker_data = MarkerSerializer(rm.marker).data
            marker_data["sequence"] = rm.sequence
            markers_with_sequence.append(marker_data)

        return markers_with_sequence


class RouteListFilterSerializer(serializers.Serializer):
    # 경로 목록 조회의 쿼리 파라미터 유효성 검사 시리얼라이저
    user_id = serializers.IntegerField(required=False)
    is_public = serializers.BooleanField(required=False)
