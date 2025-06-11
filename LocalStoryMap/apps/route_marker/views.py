# apps/route_marker/views.py
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import RouteMarker
from .serializers import (
    RouteMarkerBulkUpdateSerializer,
    RouteMarkerCreateSerializer,
    RouteMarkerSerializer,
    RouteMarkerUpdateSerializer,
)
from .services import RouteMarkerService


class RouteMarkerViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        # GET /api/route-markers: 경로-마커 연결 목록 조회
        filters = {
            "route_id": request.query_params.get("route_id"),
            "marker_id": request.query_params.get("marker_id"),
        }
        connections = RouteMarkerService.list_connections(
            user=request.user, filters=filters
        )
        serializer = RouteMarkerSerializer(connections, many=True)
        return Response(serializer.data)

    def create(self, request):
        # POST /api/route-markers: 경로에 마커 연결
        try:
            connection = RouteMarkerService.create_connection(
                request=request, data=request.data
            )
            serializer = RouteMarkerSerializer(connection)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        # PUT /api/route-markers/{route_marker_id}: 연결 정보 수정
        route_marker = get_object_or_404(RouteMarker, pk=pk)
        try:
            updated_connection = RouteMarkerService.update_connection(
                user=request.user, route_marker=route_marker, data=request.data
            )
            serializer = RouteMarkerSerializer(updated_connection)
            return Response(serializer.data)
        except PermissionError as e:
            return Response({"error": str(e)}, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        # DELETE /api/route-markers/{route_marker_id}: 연결 해제
        route_marker = get_object_or_404(RouteMarker, pk=pk)
        try:
            RouteMarkerService.delete_connection(
                user=request.user, route_marker=route_marker
            )
            return Response(status=status.HTTP_204_NO_CONTENT)
        except PermissionError as e:
            return Response({"error": str(e)}, status=status.HTTP_403_FORBIDDEN)

    @action(detail=False, methods=["put"], url_path="bulk-update")
    def bulk_update(self, request):
        # PUT /api/route-markers/bulk-update: 순서 일괄 변경
        serializer = RouteMarkerBulkUpdateSerializer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid(raise_exception=True):
            validated_data = serializer.validated_data
            try:
                RouteMarkerService.bulk_reorder_markers(
                    user=request.user,
                    route_id=validated_data["route_id"],
                    markers_data=validated_data["markers"],
                )
                return Response({"success": True, "message": "마커 순서가 성공적으로 변경되었습니다."})
            except Exception as e:
                return Response(
                    {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
