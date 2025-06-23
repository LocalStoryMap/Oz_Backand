from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.marker.models import Marker
from apps.story.models import Story
from apps.users.models import User

from .serializers import (
    MarkerSearchResultSerializer,
    StorySearchResultSerializer,
    UserSearchResultSerializer,
)


class SearchView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        tags=["search"],
        manual_parameters=[
            openapi.Parameter(
                "query",
                openapi.IN_QUERY,
                description="검색어",
                type=openapi.TYPE_STRING,
                required=True,
            )
        ],
        operation_summary="통합 검색",
        operation_description="유저 닉네임, 스토리 제목, 마커 제목 등을 통합 검색합니다.",
    )
    def get(self, request):
        query = request.query_params.get("query", "").strip()
        if not query:
            return Response({"detail": "검색어(query)가 필요합니다."}, status=400)

        # 닉네임으로 유저 검색
        users = User.objects.filter(nickname__icontains=query)
        user_results = UserSearchResultSerializer(users, many=True).data

        # 마커 제목 검색
        markers = Marker.objects.filter(marker_name__icontains=query)
        marker_results = MarkerSearchResultSerializer(markers, many=True).data

        # 스토리 제목으로 검색
        stories = Story.objects.filter(title__icontains=query)
        story_results = StorySearchResultSerializer(stories, many=True).data

        return Response(
            {
                "users": user_results,
                "markers": marker_results,
                "stories": story_results,
            }
        )
