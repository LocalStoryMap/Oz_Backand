# apps/route_like/views.py
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action

from .serializers import RouteLikeSerializer, RouteLikeStatusSerializer
from .services import RouteLikeService


class RouteLikeViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request, route_id=None):
        # GET /routes/{route_id}/likes/ - 경로 좋아요 목록
        likes = RouteLikeService.get_route_likes_list(route_id=int(route_id))
        serializer = RouteLikeSerializer(likes, many=True)
        return Response({
            'success': True,
            'data': serializer.data
        })

    @action(detail=False, methods=['get'], url_path='status')
    def like_status(self, request, route_id=None):
        # GET /routes/{route_id}/likes/status/ - 좋아요 상태 확인
        status_data = RouteLikeService.get_like_status(
            user=request.user,
            route_id=int(route_id)
        )
        serializer = RouteLikeStatusSerializer(status_data)
        return Response({
            'success': True,
            'data': serializer.data
        })

    @action(detail=False, methods=['post'], url_path='toggle')
    def toggle_like(self, request, route_id=None):
        # POST /routes/{route_id}/likes/toggle/ - 좋아요 토글
        result = RouteLikeService.toggle_like(
            user=request.user,
            route_id=int(route_id)
        )

        return Response({
            'success': True,
            'action': result['action'],
            'total_likes': result['total_likes'],
            'message': f"좋아요가 {'추가' if result['action'] == 'added' else '제거'}되었습니다."
        }, status=status.HTTP_200_OK)
