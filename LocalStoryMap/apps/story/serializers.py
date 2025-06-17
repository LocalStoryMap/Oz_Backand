from rest_framework import serializers

from apps.story.models import CommentLike, Story, StoryComment, StoryLike


class StorySerializer(serializers.ModelSerializer):
    user_nickname = serializers.CharField(source="user.nickname", read_only=True)
    user_profile_image = serializers.ImageField(
        source="user.profile_image", read_only=True
    )

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


class CommentSerializer(serializers.ModelSerializer):
    user_nickname = serializers.CharField(source="user.nickname", read_only=True)
    user_profile_image = serializers.ImageField(
        source="user.profile_image", read_only=True
    )
    parent = serializers.PrimaryKeyRelatedField(
        queryset=StoryComment.objects.all(),
        write_only=True,
        required=False,
        allow_null=True,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "story" in self.context:
            story = self.context["story"]
            self.fields["parent"].queryset = StoryComment.objects.filter(story=story)

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
            "parent",
        ]
        read_only_fields = [
            "comment_id",
            "story_id",
            "user_nickname",
            "user_profile_image",
            "created_at",
            "updated_at",
        ]


class StoryLikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoryLike
        fields = ["story", "user", "created_at"]
        read_only_fields = fields


class CommentLikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommentLike
        fields = ["comment", "user", "created_at"]
        read_only_fields = fields
