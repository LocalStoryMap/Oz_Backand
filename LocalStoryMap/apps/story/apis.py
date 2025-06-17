from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.story.serializers import (
    CommentLikeSerializer,
    CommentSerializer,
    StoryLikeSerializer,
    StorySerializer,
)


class StoryAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="스토리 목록 조회",
        responses={
            200: openapi.Response(description="OK", schema=StorySerializer(many=True))
        },
        tags=["스토리"],
    )
    def get(self, request, *args, **kwargs):
        # 스토리 목록을 조회합니다 (필터링, 정렬, 페이징 지원 예정)
        # 로직 작성 예정
        pass

    @swagger_auto_schema(
        operation_summary="스토리 생성",
        request_body=StorySerializer,
        responses={
            201: openapi.Response(description="Created", schema=StorySerializer)
        },
        tags=["스토리"],
    )
    def post(self, request, *args, **kwargs):
        # 새로운 스토리를 생성합니다 (제목, 내용, 마커, 이모티콘 등)
        # 로직 작성 예정
        pass


class StoryDetailAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="특정 스토리 조회",
        responses={200: openapi.Response(description="OK", schema=StorySerializer)},
        tags=["스토리"],
    )
    def get(self, request, story_id, *args, **kwargs):
        # 특정 스토리를 조회합니다 (조회수 증가 포함)
        # 로직 작성 예정
        pass

    @swagger_auto_schema(
        operation_summary="스토리 수정",
        request_body=StorySerializer,
        responses={200: openapi.Response(description="OK", schema=StorySerializer)},
        tags=["스토리"],
    )
    def patch(self, request, story_id, *args, **kwargs):
        # 스토리의 일부 필드를 수정합니다 (제목, 내용, 이모티콘 등)
        # 로직 작성 예정
        pass

    @swagger_auto_schema(
        operation_summary="스토리 삭제",
        responses={204: "No Content"},
        tags=["스토리"],
    )
    def delete(self, request, story_id, *args, **kwargs):
        # 스토리를 소프트 삭제합니다 (is_deleted = True로 설정)
        # 로직 작성 예정
        pass


class CommentListAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="댓글 목록 조회",
        responses={
            200: openapi.Response(description="OK", schema=CommentSerializer(many=True))
        },
        tags=["댓글"],
    )
    def get(self, request, story_id, *args, **kwargs):
        # 특정 스토리의 댓글 목록을 조회합니다 (대댓글 포함)
        # 로직 작성 예정
        pass

    @swagger_auto_schema(
        operation_summary="댓글 생성",
        request_body=CommentSerializer,
        responses={
            201: openapi.Response(description="Created", schema=CommentSerializer)
        },
        tags=["댓글"],
    )
    def post(self, request, story_id, *args, **kwargs):
        # 새로운 댓글을 생성합니다 (일반 댓글 또는 대댓글)
        # 로직 작성 예정
        pass


class CommentDetailAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="댓글 수정",
        request_body=CommentSerializer,
        responses={200: openapi.Response(description="OK", schema=CommentSerializer)},
        tags=["댓글"],
    )
    def patch(self, request, comment_id, *args, **kwargs):
        # 댓글 내용을 수정합니다 (작성자만 수정 가능)
        # 로직 작성 예정
        pass

    @swagger_auto_schema(
        operation_summary="댓글 삭제",
        responses={204: "No Content"},
        tags=["댓글"],
    )
    def delete(self, request, comment_id, *args, **kwargs):
        # 댓글을 소프트 삭제합니다 (작성자 또는 관리자만 삭제 가능)
        # 로직 작성 예정
        pass


class StoryLikeListAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="스토리 좋아요 목록 조회",
        responses={
            200: openapi.Response(
                description="OK", schema=StoryLikeSerializer(many=True)
            )
        },
        tags=["스토리 좋아요"],
    )
    def get(self, request, story_id, *args, **kwargs):
        # 특정 스토리를 좋아요한 사용자 목록을 조회합니다
        # 로직 작성 예정
        pass


class StoryLikeDetailAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="스토리 좋아요 추가",
        request_body=StoryLikeSerializer,
        responses={
            201: openapi.Response(description="Created", schema=StoryLikeSerializer)
        },
        tags=["스토리 좋아요"],
    )
    def post(self, request, story_id, user_id, *args, **kwargs):
        # 스토리에 좋아요를 추가합니다 (중복 좋아요 방지)
        # 로직 작성 예정
        pass

    @swagger_auto_schema(
        operation_summary="스토리 좋아요 삭제",
        responses={204: "No Content"},
        tags=["스토리 좋아요"],
    )
    def delete(self, request, story_id, user_id, *args, **kwargs):
        # 스토리 좋아요를 취소합니다 (본인이 좋아요한 것만 취소 가능)
        # 로직 작성 예정
        pass


class CommentLikeListAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="댓글 좋아요 목록 조회",
        responses={
            200: openapi.Response(
                description="OK", schema=CommentLikeSerializer(many=True)
            )
        },
        tags=["댓글 좋아요"],
    )
    def get(self, request, comment_id, *args, **kwargs):
        # 특정 댓글을 좋아요한 사용자 목록을 조회합니다
        # 로직 작성 예정
        pass


class CommentLikeDetailAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="댓글 좋아요 추가",
        request_body=CommentLikeSerializer,
        responses={
            201: openapi.Response(description="Created", schema=CommentLikeSerializer)
        },
        tags=["댓글 좋아요"],
    )
    def post(self, request, comment_id, user_id, *args, **kwargs):
        # 댓글에 좋아요를 추가합니다 (중복 좋아요 방지)
        # 로직 작성 예정
        pass

    @swagger_auto_schema(
        operation_summary="댓글 좋아요 삭제",
        responses={204: "No Content"},
        tags=["댓글 좋아요"],
    )
    def delete(self, request, comment_id, user_id, *args, **kwargs):
        # 댓글 좋아요를 취소합니다 (본인이 좋아요한 것만 취소 가능)
        # 로직 작성 예정
        pass
