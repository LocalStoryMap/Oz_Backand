# apps/marker_like/views.py
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action

from .serializers import MarkerLikeSerializer, MarkerLikeStatusSerializer
from .services import MarkerLikeService


class MarkerLikeViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request, marker_id=None):
        # GET /api/markers/{marker_id}/likes/ - 마커 좋아요 목록
        likes = MarkerLikeService.get_marker_likes_list(marker_id=int(marker_id))
        serializer = MarkerLikeSerializer(likes, many=True)
        return Response({
            'success': True,
            'data': serializer.data
        })

    @action(detail=False, methods=['get'], url_path='status')
    def like_status(self, request, marker_id=None):
        # GET /api/markers/{marker_id}/likes/status/ - 좋아요 상태 확인
        status_data = MarkerLikeService.get_like_status(
            user=request.user,
            marker_id=int(marker_id)
        )
        serializer = MarkerLikeStatusSerializer(status_data)
        return Response({
            'success': True,
            'data': serializer.data
        })

    @action(detail=False, methods=['post'], url_path='toggle')
    def toggle_like(self, request, marker_id=None):
        # POST /api/markers/{marker_id}/likes/toggle/ - 좋아요 토글
        result = MarkerLikeService.toggle_like(
            user=request.user,
            marker_id=int(marker_id)
        )

        return Response({
            'success': True,
            'action': result['action'],
            'total_likes': result['total_likes'],
            'message': f"좋아요가 {'추가' if result['action'] == 'added' else '제거'}되었습니다."
        }, status=status.HTTP_200_OK)
