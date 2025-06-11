from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import SearchHistory
from .serializers import SearchHistorySerializer


class SearchHistoryViewSet(viewsets.ModelViewSet):
    """
    검색 기록 CRUD
    """

    serializer_class = SearchHistorySerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="검색 기록 목록 조회",
        operation_description="현재 사용자의 검색 기록 목록을 조회합니다.",
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="검색 기록 생성",
        operation_description="현재 사용자에 대한 새로운 검색 기록을 생성합니다.",
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return SearchHistory.objects.none()
        return SearchHistory.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
