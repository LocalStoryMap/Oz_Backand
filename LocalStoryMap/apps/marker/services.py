# apps/marker/services.py
import math

from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404
from haversine import Unit, haversine

from .models import Marker
from .serializers import MarkerSerializer


class MarkerService:
    @staticmethod
    def get_marker(marker_id: int) -> Marker:
        # 특정 마커 조회
        return get_object_or_404(Marker, pk=marker_id)

    @staticmethod
    def list_markers(filters: dict, page: int = 1, limit: int = 20):
        # 조건에 맞는 마커 목록 조회 (필터링 및 페이지네이션)
        queryset = Marker.objects.all().order_by("-created_at")

        # 레이어(관광명소/맛집/카페 등) 필터 추가
        if layer := filters.get("layer"):
            queryset = queryset.filter(layer=layer)

        # 검색어 필터
        # (:=)를 사용하여 filters 딕셔너리에서 'search_term'을 가져오고, 그 값이 존재하면 if문 안의 로직을 실행
        if search_term := filters.get("search_term"):
            queryset = queryset.filter(
                Q(marker_name__icontains=search_term)
                | Q(description__icontains=search_term)  # OR
                | Q(adress__icontains=search_term)  # OR
            )

        if story_id := filters.get("story_id"):
            queryset = queryset.filter(story_id=story_id)

        # 위치 기반 필터 (단순 거리 계산 예시)
        final_markers = []
        if (lat := filters.get("latitude")) and (lng := filters.get("longitude")):
            radius = filters.get("radius", 10.0)  # 단위: km
            center_point = (lat, lng)

            # 1. 성능을 위한 1차 'Bounding Box' 필터링 (DB에서 빠르게 후보군 추리기)
            lat_diff = radius / 111.0
            lng_diff = radius / (111.0 * abs(math.cos(math.radians(lat))))

            lat_min, lat_max = lat - lat_diff, lat + lat_diff
            lng_min, lng_max = lng - lng_diff, lng + lng_diff

            candidate_markers = queryset.filter(
                latitude__range=(lat_min, lat_max), longitude__range=(lng_min, lng_max)
            )

            # 2. 1차 필터링된 후보군에 대해 정확한 Haversine 거리 계산 (Python에서 정밀 필터링)
            for marker in candidate_markers:
                marker_point = (marker.latitude, marker.longitude)
                distance = haversine(center_point, marker_point, unit=Unit.KILOMETERS)

                if distance <= radius:
                    final_markers.append(marker)

            # 페이지네이션 대상은 최종 필터링된 리스트
            target_list = final_markers
        else:
            # 위치 필터가 없으면 전체 쿼리셋을 대상으로 함
            target_list = list(queryset)

        paginator = Paginator(target_list, limit)
        page_obj = paginator.get_page(page)

        return {
            "markers": page_obj.object_list,
            "pagination": {
                "current_page": page_obj.number,
                "total_pages": paginator.num_pages,
                "total_items": paginator.count,
                "items_per_page": limit,
            },
        }

    @staticmethod
    def create_marker(data: dict) -> Marker:
        # 새로운 마커 생성
        serializer = MarkerSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        return serializer.save()

    @staticmethod
    def update_marker(marker: Marker, data: dict) -> Marker:
        # 기존 마커 정보 수정
        serializer = MarkerSerializer(
            instance=marker, data=data, partial=True
        )  # partial=True: 부분 수정(PATCH)을 허용
        serializer.is_valid(raise_exception=True)
        return serializer.save()

    @staticmethod
    def delete_marker(marker: Marker) -> None:
        # 마커 삭제
        marker.delete()
