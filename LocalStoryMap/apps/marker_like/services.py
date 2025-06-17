# apps/marker_like/services.py
from django.db import transaction
from django.shortcuts import get_object_or_404
from .models import MarkerLike
from apps.marker.models import Marker


class MarkerLikeService:
    @staticmethod
    def get_like_status(user, marker_id: int):
        # 사용자의 마커 좋아요 상태 확인
        marker = get_object_or_404(Marker, pk=marker_id)
        like = MarkerLike.objects.filter(user=user, marker=marker, is_liked=True).first()

        return {
            'is_liked': like is not None,
            'like_id': like.id if like else None,
            'total_likes': marker.like_count  # DB의 like_count 사용
        }

    @staticmethod
    @transaction.atomic
    def toggle_like(user, marker_id: int):
        # 마커 좋아요 토글 (추가/제거)
        marker = get_object_or_404(Marker, pk=marker_id)
        like, created = MarkerLike.objects.get_or_create(
            user=user,
            marker=marker,
            defaults={'is_liked': True}
        )

        if created:
            # 새로 좋아요 생성
            marker.increment_like_count()
            action = 'added'
        else:
            # 기존 좋아요 토글
            if like.is_liked:
                like.is_liked = False
                marker.decrement_like_count()
                action = 'removed'
            else:
                like.is_liked = True
                marker.increment_like_count()
                action = 'added'
            like.save()

        return {
            'action': action,
            'like': like,
            'total_likes': marker.like_count
        }

    @staticmethod
    def get_marker_likes_list(marker_id: int):
        # 특정 마커의 좋아요 목록 조회
        marker = get_object_or_404(Marker, pk=marker_id)
        return MarkerLike.objects.filter(marker=marker, is_liked=True).select_related('user')
