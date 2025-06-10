# apps/route_marker/serializers.py
from rest_framework import serializers
from .models import RouteMarker
from apps.route.models import Route
from apps.marker.models import Marker
from apps.route.serializers import RouteSerializer
from apps.marker.serializers import MarkerSerializer


class RouteMarkerSerializer(serializers.ModelSerializer):
    # 경로-마커 연결 정보를 위한 기본 시리얼라이저
    route = RouteSerializer(read_only=True)
    marker = MarkerSerializer(read_only=True)

    class Meta:
        model = RouteMarker
        fields = [
            'id',
            'route',
            'marker',
            'sequence',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'route', 'marker']


class RouteMarkerCreateSerializer(serializers.ModelSerializer):
    # 경로-마커 연결 생성을 위한 시리얼라이저
    route_id = serializers.PrimaryKeyRelatedField(
        queryset=Route.objects.all(), source='route'
    )
    marker_id = serializers.PrimaryKeyRelatedField(
        queryset=Marker.objects.all(), source='marker'
    )

    class Meta:
        model = RouteMarker
        fields = ['route_id', 'marker_id', 'sequence']

    def validate(self, attrs):
        route = attrs.get('route')
        marker = attrs.get('marker')
        sequence = attrs.get('sequence')
        user = self.context['request'].user

        if route.user != user:
            raise serializers.ValidationError("이 경로에 마커를 추가할 권한이 없습니다.")

        if RouteMarker.objects.filter(route=route, marker=marker).exists():
            raise serializers.ValidationError("해당 마커는 이미 이 경로에 추가되어 있습니다.")

        if RouteMarker.objects.filter(route=route, sequence=sequence).exists():
            raise serializers.ValidationError(f"경로 내에서 순서 '{sequence}'는 이미 사용 중입니다.")

        return attrs


class RouteMarkerUpdateSerializer(serializers.ModelSerializer):
    # 경로-마커 연결 정보 수정을 위한 시리얼라이저

    class Meta:
        model = RouteMarker
        fields = ['sequence']

    def validate_sequence(self, value):
        route = self.instance.route
        if RouteMarker.objects.filter(route=route, sequence=value).exclude(pk=self.instance.pk).exists():
            raise serializers.ValidationError(f"경로 내에서 순서 '{value}'는 이미 사용 중입니다.")
        return value


class RouteMarkerBulkUpdateItemSerializer(serializers.Serializer):
    # 일괄 순서 변경을 위한 각 항목의 시리얼라이저
    route_marker_id = serializers.IntegerField()
    sequence = serializers.IntegerField(min_value=1)


class RouteMarkerBulkUpdateSerializer(serializers.Serializer):
    # 경로 내 마커 순서 일괄 변경을 위한 시리얼라이저
    route_id = serializers.IntegerField()
    markers = serializers.ListField(
        child=RouteMarkerBulkUpdateItemSerializer()
    )

    def validate(self, attrs):
        route_id = attrs.get('route_id')
        markers_data = attrs.get('markers', [])
        user = self.context['request'].user

        try:
            route = Route.objects.get(pk=route_id)
        except Route.DoesNotExist:
            raise serializers.ValidationError("존재하지 않는 경로입니다.")

        if route.user != user:
            raise serializers.ValidationError("이 경로의 마커 순서를 변경할 권한이 없습니다.")

        route_marker_ids = {item['route_marker_id'] for item in markers_data}
        if RouteMarker.objects.filter(id__in=route_marker_ids, route=route).count() != len(route_marker_ids):
            raise serializers.ValidationError("요청에 포함된 마커 중 일부가 해당 경로에 속하지 않습니다.")

        sequences = [item['sequence'] for item in markers_data]
        if len(sequences) != len(set(sequences)):
            raise serializers.ValidationError("요청된 순서 번호에 중복이 있습니다.")

        return attrs
