from django.shortcuts import get_object_or_404
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import permissions, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.story.models import CommentLike, Story, StoryComment, StoryLike
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
        qs = Story.objects.filter(is_deleted=False).order_by("-created_at")
        paginator = PageNumberPagination()
        # 아래 두 줄이 전역 설정을 따르게 해 줍니다
        page = paginator.paginate_queryset(qs, request, view=self)
        serializer = StorySerializer(page, many=True, context={"request": request})
        return paginator.get_paginated_response(serializer.data)

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
        serializer = StorySerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.save(user=request.user)  # 현재 로그인된 사용자를 스토리 작성자로 저장
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class StoryDetailAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="특정 스토리 조회",
        responses={200: openapi.Response(description="OK", schema=StorySerializer)},
        tags=["스토리"],
    )
    def get(self, request, story_id, *args, **kwargs):
        # 특정 스토리를 조회합니다 (조회수 증가 포함)
        story = get_object_or_404(Story, story_id=story_id, is_deleted=False)
        story.view_count += 1
        story.save(update_fields=["view_count"])
        serializer = StorySerializer(story, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="스토리 수정",
        request_body=StorySerializer,
        responses={200: openapi.Response(description="OK", schema=StorySerializer)},
        tags=["스토리"],
    )
    def patch(self, request, story_id, *args, **kwargs):
        # 스토리의 일부 필드를 수정합니다 (제목, 내용, 이모티콘 등)
        story = get_object_or_404(Story, story_id=story_id, is_deleted=False)

        # 권한 확인: 현재 로그인된 사용자가 스토리의 작성자인지 확인
        if story.user != request.user:
            return Response(
                {"detail": "이 스토리를 수정할 권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN
            )

        serializer = StorySerializer(
            story, data=request.data, partial=True, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_summary="스토리 삭제",
        responses={204: "No Content"},
        tags=["스토리"],
    )
    def delete(self, request, story_id, *args, **kwargs):
        # 스토리를 소프트 삭제합니다 (is_deleted = True로 설정)
        story = get_object_or_404(Story, story_id=story_id, is_deleted=False)

        # 권한 확인: 현재 로그인된 사용자가 스토리의 작성자인지 확인
        if story.user != request.user:
            return Response(
                {"detail": "이 스토리를 삭제할 권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN
            )

        story.is_deleted = True
        story.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


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
        story = get_object_or_404(Story, story_id=story_id, is_deleted=False)
        comments = StoryComment.objects.filter(
            story=story, is_deleted=False, parent__isnull=True
        ).order_by(
            "created_at"
        )  # 최상위 댓글만 조회
        serializer = CommentSerializer(
            comments, many=True, context={"request": request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

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
        story = get_object_or_404(Story, story_id=story_id, is_deleted=False)
        serializer = CommentSerializer(
            data=request.data, context={"request": request, "story": story}
        )
        if serializer.is_valid():
            serializer.save(user=request.user, story=story)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CommentDetailAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="댓글 수정",
        request_body=CommentSerializer,
        responses={200: openapi.Response(description="OK", schema=CommentSerializer)},
        tags=["댓글"],
    )
    def patch(self, request, story_id, comment_id, *args, **kwargs):
        # 댓글 내용을 수정합니다 (작성자만 수정 가능)
        story = get_object_or_404(Story, story_id=story_id, is_deleted=False)
        comment = get_object_or_404(
            StoryComment, comment_id=comment_id, is_deleted=False, story=story
        )

        # 권한 확인: 현재 로그인된 사용자가 댓글의 작성자인지 확인
        if comment.user != request.user:
            return Response(
                {"detail": "이 댓글을 수정할 권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN
            )

        serializer = CommentSerializer(
            comment, data=request.data, partial=True, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_summary="댓글 삭제",
        responses={204: "No Content"},
        tags=["댓글"],
    )
    def delete(self, request, story_id, comment_id, *args, **kwargs):
        # 댓글을 소프트 삭제합니다 (작성자 또는 관리자만 삭제 가능)
        story = get_object_or_404(Story, story_id=story_id, is_deleted=False)
        comment = get_object_or_404(
            StoryComment, comment_id=comment_id, is_deleted=False, story=story
        )

        # 권한 확인: 현재 로그인된 사용자가 댓글의 작성자인지 확인
        if comment.user != request.user:
            return Response(
                {"detail": "이 댓글을 삭제할 권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN
            )

        comment.is_deleted = True
        comment.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class StoryLikeAPIView(APIView):
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
        story = get_object_or_404(Story, story_id=story_id, is_deleted=False)
        likes = StoryLike.objects.filter(story=story)
        serializer = StoryLikeSerializer(likes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="스토리 좋아요 추가",
        request_body=StoryLikeSerializer,
        responses={
            201: openapi.Response(description="Created", schema=StoryLikeSerializer)
        },
        tags=["스토리 좋아요"],
    )
    def post(self, request, story_id, *args, **kwargs):
        # 스토리에 좋아요를 추가합니다 (중복 좋아요 방지)
        story = get_object_or_404(Story, story_id=story_id, is_deleted=False)

        # 중복 좋아요 방지
        if StoryLike.objects.filter(story=story, user=request.user).exists():
            return Response(
                {"detail": "이미 좋아요를 눌렀습니다."}, status=status.HTTP_409_CONFLICT
            )

        story_like = StoryLike.objects.create(story=story, user=request.user)

        # like_count 동기화
        story.like_count += 1
        story.save(update_fields=["like_count"])

        serializer = StoryLikeSerializer(story_like)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        operation_summary="스토리 좋아요 삭제",
        responses={204: "No Content"},
        tags=["스토리 좋아요"],
    )
    def delete(self, request, story_id, *args, **kwargs):
        # 스토리 좋아요를 취소합니다 (본인이 좋아요한 것만 취소 가능)
        story = get_object_or_404(Story, story_id=story_id, is_deleted=False)

        story_like = get_object_or_404(StoryLike, story=story, user=request.user)
        story_like.delete()

        # like_count 동기화
        story.like_count -= 1
        story.save(update_fields=["like_count"])

        return Response(status=status.HTTP_204_NO_CONTENT)


class CommentLikeAPIView(APIView):
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
    def get(self, request, story_id, comment_id, *args, **kwargs):
        # 특정 댓글을 좋아요한 사용자 목록을 조회합니다
        story = get_object_or_404(Story, story_id=story_id, is_deleted=False)
        comment = get_object_or_404(
            StoryComment, comment_id=comment_id, is_deleted=False, story=story
        )
        likes = CommentLike.objects.filter(comment=comment)
        serializer = CommentLikeSerializer(likes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="댓글 좋아요 추가",
        request_body=CommentLikeSerializer,
        responses={
            201: openapi.Response(description="Created", schema=CommentLikeSerializer)
        },
        tags=["댓글 좋아요"],
    )
    def post(self, request, story_id, comment_id, *args, **kwargs):
        # 댓글에 좋아요를 추가합니다 (중복 좋아요 방지)
        story = get_object_or_404(Story, story_id=story_id, is_deleted=False)
        comment = get_object_or_404(
            StoryComment, comment_id=comment_id, is_deleted=False, story=story
        )

        # 중복 좋아요 방지
        if CommentLike.objects.filter(comment=comment, user=request.user).exists():
            return Response(
                {"detail": "이미 좋아요를 눌렀습니다."}, status=status.HTTP_409_CONFLICT
            )

        comment_like = CommentLike.objects.create(comment=comment, user=request.user)

        # like_count 동기화
        comment.like_count += 1
        comment.save(update_fields=["like_count"])

        serializer = CommentLikeSerializer(comment_like)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        operation_summary="댓글 좋아요 삭제",
        responses={204: "No Content"},
        tags=["댓글 좋아요"],
    )
    def delete(self, request, story_id, comment_id, *args, **kwargs):
        # 댓글 좋아요를 취소합니다 (본인이 좋아요한 것만 취소 가능)
        story = get_object_or_404(Story, story_id=story_id, is_deleted=False)
        comment = get_object_or_404(
            StoryComment, comment_id=comment_id, is_deleted=False, story=story
        )

        comment_like = get_object_or_404(
            CommentLike, comment=comment, user=request.user
        )
        comment_like.delete()

        # like_count 동기화
        comment.like_count -= 1
        comment.save(update_fields=["like_count"])

        return Response(status=status.HTTP_204_NO_CONTENT)
