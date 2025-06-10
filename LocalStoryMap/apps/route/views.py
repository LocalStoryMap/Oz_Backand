# apps/route/views.py
from rest_framework import viewsets, status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .models import Route
from .serializers import (
    RouteSerializer,
    RouteListFilterSerializer,
    RouteWithOrderedMarkersSerializer,
)
from .services import RouteService


class RouteViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def list(self, request):
        # GET /routes: 경로 목록 조회
        filter_serializer = RouteListFilterSerializer(data=request.query_params)
        filter_serializer.is_valid(raise_exception=True)

        page = int(request.query_params.get('page', 1))
        limit = int(request.query_params.get('limit', 20))

        result = RouteService.list_routes(
            user=request.user,
            filters=filter_serializer.validated_data,
            page=page,
            limit=limit
        )

        serialized_data = RouteSerializer(result["routes"], many=True).data

        return Response({
            "success": True,
            "data": serialized_data,
            "pagination": result["pagination"]
        })

    def create(self, request):
        # POST /routes: 경로 생성
        try:
            route = RouteService.create_route(user=request.user, data=request.data)
            serializer = RouteSerializer(route)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        # GET /routes/{route_id}: 특정 경로 조회
        try:
            route = RouteService.get_route(user=request.user, route_id=pk)

            # include_markers 파라미터에 따라 다른 시리얼라이저 사용
            if request.query_params.get('include_markers', 'true').lower() == 'true':
                serializer = RouteWithOrderedMarkersSerializer(route)
            else:
                serializer = RouteSerializer(route)

            return Response({"success": True, "data": serializer.data})
        except PermissionError as e:
            return Response({"error": str(e)}, status=status.HTTP_403_FORBIDDEN)
        except Route.DoesNotExist:
            return Response({"error": "경로를 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)

    def update(self, request, pk=None):
        # PUT /routes/{route_id}: 특정 경로 수정
        try:
            route = get_object_or_404(Route, pk=pk)
            updated_route = RouteService.update_route(user=request.user, route=route, data=request.data)
            serializer = RouteSerializer(updated_route)
            return Response(serializer.data)
        except PermissionError as e:
            return Response({"error": str(e)}, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        # DELETE /routes/{route_id}: 특정 경로 삭제
        try:
            route = get_object_or_404(Route, pk=pk)
            RouteService.delete_route(user=request.user, route=route)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except PermissionError as e:
            return Response({"error": str(e)}, status=status.HTTP_403_FORBIDDEN)
