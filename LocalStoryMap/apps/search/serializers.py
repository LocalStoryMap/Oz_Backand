from rest_framework import serializers

from .models import SearchHistory


class SearchHistorySerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True, label="ID")
    query = serializers.CharField(label="검색어")
    searched_at = serializers.DateTimeField(read_only=True, label="검색 일시")

    class Meta:
        model = SearchHistory
        fields = ["id", "query", "searched_at"]
        read_only_fields = ["id", "searched_at"]
