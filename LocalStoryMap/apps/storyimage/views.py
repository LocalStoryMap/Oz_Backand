from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import parsers, permissions, viewsets

from .models import StoryImage
from .serializers import ImageSerializer


class StoryImageViewSet(viewsets.ModelViewSet):
    queryset = StoryImage.objects.all()
    serializer_class = ImageSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]

    def get_serializer_context(self):
        return {"request": self.request}

    def get_queryset(self):
        # 1) nested router가 전달하는 story_pk가 있으면 해당 스토리 이미지만 리턴
        story_pk = self.kwargs.get("story_pk")
        if story_pk is not None:
            return self.queryset.filter(story_id=story_pk)

        # 2) 그렇지 않으면 전체 Image 리스트
        return self.queryset

    @swagger_auto_schema(tags=["스토리 이미지"],
                         operation_summary="스토리 이미지",
                         responses={
                             200: openapi.Response(
                                 description="이미지 불러오기 성공.", schema=ImageSerializer(many=True)
                                )
                            }
                        )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(tags=["스토리 이미지"],
                         operation_summary="스토리 이미지",
                         responses={
                             201: openapi.Response(
                                 description="이미지 생성 성공.", schema=ImageSerializer(many=True)
                                )
                             }
                         )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(tags=["스토리 이미지"],
                         operation_summary="스토리 이미지",
                         responses={
                             204: openapi.Response(
                                 description="이미지 생성 성공.", schema=ImageSerializer(many=True)
                                )
                             }
                         )
    def delete(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
