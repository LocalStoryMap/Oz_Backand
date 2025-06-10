# apps/route/services.py
from django.db.models import Q
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
from .models import Route
from .serializers import (
    RouteCreateSerializer,
    RouteUpdateSerializer,
)

class RouteService:
    def get_route(user, route_id: int) -> Route:
        # 특정 경로 조회
        route = get_object_or_404(Route, pk=route_id)
        if not route.is_public and route.user != user:
            raise PermissionError("이 경로를 볼 권한이 없습니다.")
        return route

    def list_routes(user, filters: dict, page: int = 1, limit: int = 20):
        # 조건에 맞는 경로 목록 조회

        # 공개된 경로 또는 내가 작성한 경로만 조회
        queryset = Route.objects.filter(Q(is_public=True) | Q(user=user))

        if user_id := filters.get('user_id'):
            queryset = queryset.filter(user_id=user_id)

        if (is_public := filters.get('is_public')) is not None:
            queryset = queryset.filter(is_public=is_public)

        paginator = Paginator(queryset.distinct(), limit)
        page_obj = paginator.get_page(page)

        return {
            "routes": page_obj.object_list,
            "pagination": {
                "current_page": page_obj.number,
                "total_pages": paginator.num_pages,
                "total_items": paginator.count,
                "items_per_page": limit,
            }
        }

    def create_route(user, data: dict) -> Route:
        # 새로운 경로 생성
        serializer = RouteCreateSerializer(data=data, context={'request': {'user': user}})
        serializer.is_valid(raise_exception=True)
        return serializer.save(user=user)

    def update_route(user, route: Route, data: dict) -> Route:
        # 기존 경로 수정
        if route.user != user:
            raise PermissionError("이 경로를 수정할 권한이 없습니다.")

        serializer = RouteUpdateSerializer(instance=route, data=data, partial=True, context={'request': {'user': user}})
        serializer.is_valid(raise_exception=True)
        return serializer.save()

    def delete_route(user, route: Route) -> None:
        # 경로 삭제
        if route.user != user:
            raise PermissionError("이 경로를 삭제할 권한이 없습니다.")
        route.delete()