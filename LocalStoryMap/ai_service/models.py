from django.db import models


class Location(models.Model):
    name = models.CharField(max_length=200)
    # 여행지 상세 설명 원문. 이미 백엔드 팀원이 채워서 DB에 저장되어 있음.
    detail_text = models.TextField()
    # (선택) 요약문을 캐싱하려면 아래 필드를 추가할 수 있음
    summary_text = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
