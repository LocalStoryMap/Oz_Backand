# apps/route_like/services.py
from django.db import transaction
from django.shortcuts import get_object_or_404
from .models import RouteLike
from apps.route.models import Route


class RouteLikeService:
    @staticmethod
    def get_like_status(user, route_id: int):
        # 사용자의 경로 좋아요 상태 확인
        route = get_object_or_404(Route, pk=route_id)
        like = RouteLike.objects.filter(user=user, route=route, is_liked=True).first()

        return {
            'is_liked': like is not None,
            'like_id': like.id if like else None,
            'total_likes': route.like_count  # DB의 like_count 사용
        }

    @staticmethod
    @transaction.atomic
    def toggle_like(user, route_id: int):
        # 경로 좋아요 토글 (추가/제거)
        route = get_object_or_404(Route, pk=route_id)
        like, created = RouteLike.objects.get_or_create(
            user=user,
            route=route,
            defaults={'is_liked': True}
        )

        if created:
            # 새로 좋아요 생성
            route.increment_like_count()
            action = 'added'
        else:
            # 기존 좋아요 토글
            if like.is_liked:
                like.is_liked = False
                route.decrement_like_count()
                action = 'removed'
            else:
                like.is_liked = True
                route.increment_like_count()
                action = 'added'
            like.save()

        return {
            'action': action,
            'like': like,
            'total_likes': route.like_count
        }

    @staticmethod
    def get_route_likes_list(route_id: int):
        # 특정 경로의 좋아요 목록 조회
        route = get_object_or_404(Route, pk=route_id)
        return RouteLike.objects.filter(route=route, is_liked=True).select_related('user')
