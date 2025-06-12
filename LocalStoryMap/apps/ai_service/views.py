from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Location
from .serializers import ChatRequestSerializer, SummarizeRequestSerializer
from .utils.clova_client import ClovaClient


class SummarizeAPIView(APIView):
    """
    POST /api/summarize/
    {
        "location_id": 123
    }
    -->
    {
        "summary": "여기에 요약문"
    }
    또는
    {
        "raw_text": "직접 보낼 긴 텍스트"
    }
    """

    def post(self, request, *args, **kwargs):
        serializer = SummarizeRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        clova = ClovaClient()

        location_id = serializer.validated_data.get("location_id")
        raw_text = serializer.validated_data.get("raw_text")

        # 1) location_id가 있으면 DB에서 원문 조회
        if location_id:
            location_obj = get_object_or_404(Location, pk=location_id)
            text_to_summarize = location_obj.detail_text
        else:
            text_to_summarize = raw_text

        # 2) Clova에 요약 요청
        try:
            summary = clova.summarize_text(text=text_to_summarize)
        except Exception as e:
            # Clova 호출 에러 처리
            return Response(
                {"error": f"Clova 요약 API 호출 실패: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # 3) (선택) DB 캐시에 저장하려면 여기에 로직 추가
        if location_id:
            # 예: 처음 요약인 경우 저장
            if not location_obj.summary_text:
                location_obj.summary_text = summary
                location_obj.save(update_fields=["summary_text"])

        return Response({"summary": summary}, status=status.HTTP_200_OK)


class ChatAPIView(APIView):
    """
    POST /api/chat/
    {
        "messages": [
            { "role": "system", "content": "너는 ~~~"},
            { "role": "user", "content": "안녕!"},
            ...
        ]
    }
    -->
    {
        "reply": "봇이 응답한 내용"
    }
    """

    def post(self, request, *args, **kwargs):
        serializer = ChatRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        clova = ClovaClient()

        messages = serializer.validated_data["messages"]

        try:
            reply = clova.chat(messages=messages)
        except Exception as e:
            return Response(
                {"error": f"Clova Chat API 호출 실패: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response({"reply": reply}, status=status.HTTP_200_OK)
