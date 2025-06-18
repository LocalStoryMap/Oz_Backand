# apps/marker/views.py
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from .models import Marker
from .serializers import MarkerListFilterSerializer, MarkerSerializer
from .services import MarkerService


class MarkerViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]  # 인증된 사용자는 R/W, 비인증 사용자는 R-Only

    # router.register를 사용하기 위해 ViewSet의 메서드 사용
    def list(self, request):
        # GET /markers: 마커 목록 조회
        # 쿼리 파라미터 유효성 검사
        filter_serializer = MarkerListFilterSerializer(data=request.query_params)
        filter_serializer.is_valid(raise_exception=True)

        page = int(request.query_params.get("page", 1))
        limit = int(request.query_params.get("limit", 20))

        result = MarkerService.list_markers(
            filters=filter_serializer.validated_data, page=page, limit=limit
        )

        serialized_data = MarkerSerializer(
            result["markers"], many=True, context={"request": request}
        ).data

        return Response(
            {
                "success": True,
                "data": serialized_data,
                "pagination": result["pagination"],
            }
        )

    def create(self, request):
        # POST /markers: 마커 생성
        try:
            marker = MarkerService.create_marker(data=request.data)
            serializer = MarkerSerializer(marker, context={"request": request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        # GET /markers/{marker_id}: 특정 마커 조회
        marker = MarkerService.get_marker(marker_id=pk)
        serializer = MarkerSerializer(marker, context={"request": request})
        return Response(serializer.data)

    def update(self, request, pk=None):
        # PUT /markers/{marker_id}: 특정 마커 수정
        marker = MarkerService.get_marker(marker_id=pk)
        try:
            updated_marker = MarkerService.update_marker(
                marker=marker, data=request.data
            )
            serializer = MarkerSerializer(updated_marker, context={"request": request})
            return Response(serializer.data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        # DELETE /markers/{marker_id}: 특정 마커 삭제
        marker = MarkerService.get_marker(marker_id=pk)
        MarkerService.delete_marker(marker=marker)
        return Response(status=status.HTTP_204_NO_CONTENT)
