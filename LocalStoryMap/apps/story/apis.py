from django.db.models import ExpressionWrapper, F, FloatField
from django.db.models.functions import Random
from django.shortcuts import get_object_or_404
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import permissions, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.story.models import CommentLike, Story, StoryComment, StoryLike
from apps.story.serializers import (
    BasicStorySerializer,
    CommentLikeSerializer,
    CommentSerializer,
    FullStorySerializer,
    StoryLikeSerializer,
)


class StoryAPIView(APIView):
    # 전체 뷰에 "구독자면 전부 OK, 비구독자면 GET만(스토리 조회용)" 정책 적용
    # permission_classes = [SubscriberPermission]
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = PageNumberPagination

    def get_serializer_class(self):
        user = self.request.user
        # 인증되지 않은 사용자 처리
        if not user or not user.is_authenticated:
            return BasicStorySerializer
        # is_paid_user로 구독 여부 체크
        if getattr(user, "is_paid_user", False):
            return FullStorySerializer
        return BasicStorySerializer

    @swagger_auto_schema(
        operation_summary="스토리 목록 조회",
        operation_description="구독자는 FullStorySerializer, 비구독자는 BasicStorySerializer로 응답됩니다.",
        responses={
            200: openapi.Response(
                description="OK", schema=FullStorySerializer(many=True)
            )
        },
        tags=["스토리"],
    )
    def get(self, request, *args, **kwargs):
        # 1) 기본 필터링
        qs = (
            Story.objects.filter(is_deleted=False)
            .select_related("user")  # N+1 쿼리 방지
            .prefetch_related("storyimages")  # 스토리 이미지 prefetch
            .annotate(rand_val=Random())
            .annotate(  # 2) 랜덤값+조회수로 composite_score 계산
                composite_score=ExpressionWrapper(
                    F("view_count") * 0.7 + F("rand_val") * 0.3,
                    output_field=FloatField(),
                )
            )
            .order_by("-composite_score")
        )
        # 3) 페이징 - 한 번만 생성한 paginator 인스턴스 재사용
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(qs, request, view=self)
        # 4) 동적 Serializer 선택 및 응답
        SerializerClass = self.get_serializer_class()
        serializer = SerializerClass(page, many=True, context={"request": request})
        return paginator.get_paginated_response(serializer.data)

    @swagger_auto_schema(
        operation_summary="스토리 생성",
        request_body=FullStorySerializer,
        responses={
            201: openapi.Response(description="Created", schema=FullStorySerializer)
        },
        tags=["스토리"],
    )
    def post(self, request, *args, **kwargs):
        # is_paid_user=True인 경우만 이 메서드에 진입합니다.
        serializer = FullStorySerializer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


class MyStoryListAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = PageNumberPagination

    def get_serializer_class(self):
        user = self.request.user
        # is_paid_user로 구독 여부 체크
        if getattr(user, "is_paid_user", False):
            return FullStorySerializer
        return BasicStorySerializer

    @swagger_auto_schema(
        operation_summary="내가 쓴 스토리 목록 조회",
        operation_description="현재 로그인한 사용자가 작성한 스토리 목록을 조회합니다.",
        manual_parameters=[
            openapi.Parameter(
                "page",
                openapi.IN_QUERY,
                description="페이지 번호",
                type=openapi.TYPE_INTEGER,
            )
        ],
        responses={
            200: openapi.Response(
                description="OK", schema=FullStorySerializer(many=True)
            )
        },
        tags=["스토리"],
    )
    def get(self, request, *args, **kwargs):
        # 현재 로그인한 사용자의 스토리를 필터링
        qs = (
            Story.objects.filter(user=request.user, is_deleted=False)
            .select_related("user")
            .prefetch_related("storyimages")
            .order_by("-created_at")
        )

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(qs, request, view=self)

        SerializerClass = self.get_serializer_class()
        serializer = SerializerClass(page, many=True, context={"request": request})

        return paginator.get_paginated_response(serializer.data)


class MarkerStoryListAPIView(APIView):
    # 전체 뷰에 "구독자면 전부 OK, 비구독자면 GET만(스토리 조회용)" 정책 적용
    # permission_classes = [SubscriberPermission]
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        user = self.request.user
        # 인증되지 않은 사용자 처리
        if not user or not user.is_authenticated:
            return BasicStorySerializer
        if getattr(user, "is_paid_user", False):
            return FullStorySerializer
        return BasicStorySerializer

    @swagger_auto_schema(
        operation_summary="특정 마커의 스토리 목록 조회",
        operation_description="구독자는 FullStorySerializer, 비구독자는 BasicStorySerializer로 응답됩니다.",
        responses={
            200: openapi.Response(
                description="OK", schema=FullStorySerializer(many=True)
            )
        },
        tags=["스토리"],
    )
    def get(self, request, marker_id, *args, **kwargs):
        # 특정 마커에 해당하는 스토리 목록을 좋아요 순으로 조회합니다 (상위 10개만 반환)
        qs = (
            Story.objects.filter(is_deleted=False, marker_id=marker_id)
            .select_related("user")
            .prefetch_related("storyimages")
            .order_by("-like_count")
        )[:10]
        SerializerClass = self.get_serializer_class()
        serializer = SerializerClass(qs, many=True, context={"request": request})
        return Response(serializer.data)


class StoryDetailAPIView(APIView):
    # 전체 뷰에 "구독자면 전부 OK, 비구독자면 GET만(스토리 조회용)" 정책 적용
    # permission_classes = [SubscriberPermission]
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        user = self.request.user
        # 인증되지 않은 사용자 처리
        if not user or not user.is_authenticated:
            return BasicStorySerializer
        if getattr(user, "is_paid_user", False):
            return FullStorySerializer
        return BasicStorySerializer

    @swagger_auto_schema(
        operation_summary="특정 스토리 조회",
        operation_description="구독자는 FullStorySerializer, 비구독자는 BasicStorySerializer로 응답됩니다.",
        responses={200: openapi.Response(description="OK", schema=FullStorySerializer)},
        tags=["스토리"],
    )
    def get(self, request, story_id, *args, **kwargs):
        # 특정 스토리를 조회합니다 (increase_view 파라미터가 true일 때만 조회수 증가)
        increase_view = (
            request.query_params.get("increase_view", "false").lower() == "true"
        )
        story = get_object_or_404(
            Story.objects.select_related("user").prefetch_related("storyimages"),
            story_id=story_id,
            is_deleted=False,
        )
        if increase_view:
            story.view_count += 1
            story.save(update_fields=["view_count"])
        SerializerClass = self.get_serializer_class()
        serializer = SerializerClass(story, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="스토리 수정",
        request_body=FullStorySerializer,
        responses={200: openapi.Response(description="OK", schema=FullStorySerializer)},
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

        serializer = FullStorySerializer(
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
        # 특정 스토리의 모든 댓글(최상위+대댓글)을 조회합니다
        story = get_object_or_404(Story, story_id=story_id, is_deleted=False)
        comments = StoryComment.objects.filter(story=story, is_deleted=False).order_by(
            "created_at"
        )  # 모든 댓글 조회
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
        serializer = CommentLikeSerializer(
            likes, many=True, context={"request": request}
        )
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

        serializer = CommentLikeSerializer(comment_like, context={"request": request})
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
