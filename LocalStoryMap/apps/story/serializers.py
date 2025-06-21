from drf_yasg.utils import swagger_serializer_method
from rest_framework import serializers

from apps.story.models import CommentLike, Story, StoryComment, StoryLike
from apps.storyimage.serializers import ImageSerializer

# 전체 목록 조회를 할때 랜덤으로
# 마커 검색 조회수 + 좋아요 순으로
# (더 나아가서 알고리즘)


class StorySerializer(serializers.ModelSerializer):
    user_nickname = serializers.CharField(source="user.nickname", read_only=True)
    user_profile_image = serializers.ImageField(
        source="user.profile_image", read_only=True
    )
    story_images = ImageSerializer(
        many=True, read_only=True, source="storyimage_set"  # 모델의 기본 related_name
    )

    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = Story
        fields = [
            "story_id",
            "user_nickname",
            "user_profile_image",
            "marker",
            "title",
            "content",
            "emoji",
            "view_count",
            "like_count",
            "created_at",
            "updated_at",
            "story_images",
            "is_liked",
        ]
        read_only_fields = [
            "story_id",
            "user_nickname",
            "user_profile_image",
            "view_count",
            "like_count",
            "created_at",
            "updated_at",
        ]

    @swagger_serializer_method(serializer_or_field=serializers.BooleanField())
    def get_is_liked(self, obj):
        user = self.context.get("request").user
        if not user or not user.is_authenticated:
            return False
        return StoryLike.objects.filter(user=user, story=obj).exists()


class CommentSerializer(serializers.ModelSerializer):
    user_nickname = serializers.CharField(source="user.nickname", read_only=True)
    user_profile_image = serializers.ImageField(
        source="user.profile_image", read_only=True
    )
    # 요청(request) 바디에서는 parent_id로 부모 댓글 ID를 받습니다.
    parent_id = serializers.PrimaryKeyRelatedField(
        queryset=StoryComment.objects.all(),
        source="parent",
        write_only=True,
        required=False,
        allow_null=True,
        help_text="(Optional) 부모 댓글의 ID",
    )
    # 응답(response)에서는 parent로 부모 댓글 ID만 보여줍니다.
    parent = serializers.IntegerField(
        source="parent.comment_id", read_only=True, help_text="(Optional) 부모 댓글의 ID"
    )
    is_liked = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # context로 전달된 story에 따라 parent_id 선택지를 제한
        if "story" in self.context:
            story = self.context["story"]
            self.fields["parent_id"].queryset = StoryComment.objects.filter(story=story)

    class Meta:
        model = StoryComment
        fields = [
            "comment_id",
            "story_id",
            "user_nickname",
            "user_profile_image",
            "content",
            "created_at",
            "updated_at",
            "parent_id",  # 요청 시 사용
            "parent",  # 응답 시 사용
            "like_count",
            "is_liked",
        ]
        read_only_fields = [
            "comment_id",
            "story_id",
            "user_nickname",
            "user_profile_image",
            "created_at",
            "updated_at",
            "parent",  # 응답 전용
            "like_count",
            "is_liked",
        ]

    @swagger_serializer_method(serializer_or_field=serializers.BooleanField())
    def get_is_liked(self, obj):
        user = self.context.get("request").user
        if not user or not user.is_authenticated:
            return False
        return CommentLike.objects.filter(user=user, comment=obj).exists()


class StoryLikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoryLike
        fields = ["story", "user", "created_at", "like_count"]
        read_only_fields = fields


class CommentLikeSerializer(serializers.ModelSerializer):
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = CommentLike
        fields = ["comment", "user", "created_at", "like_count", "is_liked"]
        read_only_fields = fields

    @swagger_serializer_method(serializer_or_field=serializers.BooleanField())
    def get_is_liked(self, obj):
        user = self.context.get("request").user
        if not user or not user.is_authenticated:
            return False
        return CommentLike.objects.filter(user=user, comment=obj.comment).exists()
