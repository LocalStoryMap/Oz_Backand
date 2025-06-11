# apps/route_marker/services.py
from django.db.models import Q

from apps.route.models import Route

from .models import RouteMarker
from .serializers import (RouteMarkerBulkUpdateSerializer,
                          RouteMarkerCreateSerializer,
                          RouteMarkerUpdateSerializer)


class RouteMarkerService:
    def list_connections(user, filters: dict):
        # 조건에 맞는 경로-마커 연결 목록 조회
        queryset = RouteMarker.objects.select_related("route", "marker").filter(
            Q(route__is_public=True) | Q(route__user=user)
        )
        if route_id := filters.get("route_id"):
            queryset = queryset.filter(route_id=route_id)
        if marker_id := filters.get("marker_id"):
            queryset = queryset.filter(marker_id=marker_id)

        return queryset.distinct()

    def create_connection(request, data: dict) -> RouteMarker:
        # 경로-마커 연결 생성
        serializer = RouteMarkerCreateSerializer(
            data=data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        return serializer.save()

    def update_connection(user, route_marker: RouteMarker, data: dict) -> RouteMarker:
        # 경로-마커 연결 정보 수정
        if route_marker.route.user != user:
            raise PermissionError("이 연결을 수정할 권한이 없습니다.")

        serializer = RouteMarkerUpdateSerializer(
            instance=route_marker, data=data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        return serializer.save()

    def delete_connection(user, route_marker: RouteMarker) -> None:
        # 경로-마커 연결 해제
        if route_marker.route.user != user:
            raise PermissionError("이 연결을 삭제할 권한이 없습니다.")
        route_marker.delete()

    def bulk_reorder_markers(user, route_id: int, markers_data: list) -> None:
        # 경로 내 마커 순서를 일괄 변경
        route = Route.objects.get(pk=route_id)

        # 모델의 reorder_sequence 클래스 메서드 활용
        new_order_list = [
            (item["route_marker_id"], item["sequence"]) for item in markers_data
        ]
        RouteMarker.reorder_sequence(route, new_order_list)
