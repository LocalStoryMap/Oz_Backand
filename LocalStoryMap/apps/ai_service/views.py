from django.shortcuts import get_object_or_404
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.marker.models import Marker

from .serializers import ChatRequestSerializer, SummarizeRequestSerializer
from .utils.clova_client import ClovaClient

clova = ClovaClient()


class SummarizeAPIView(APIView):
    """
    POST /api/ai/summarize/
    {
        "marker_id": 123
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

    @swagger_auto_schema(
        tags=["AI 기능"],
        operation_summary="상세 스토리 요약 기능",
        request_body=SummarizeRequestSerializer,
        responses={
            200: openapi.Response(
                description="요약 성공", schema=SummarizeRequestSerializer(many=True)
            )
        },
    )
    def post(self, request, *args, **kwargs):
        serializer = SummarizeRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        marker_id = serializer.validated_data.get("marker_id")
        raw_text = serializer.validated_data.get("raw_text")

        # 1) location_id가 있으면 DB에서 원문 조회
        if marker_id:
            marker_obj = get_object_or_404(Marker, pk=marker_id)
            text_to_summarize = marker_obj.description or raw_text
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
        if marker_id:
            # 예: 처음 요약인 경우 저장
            if not marker_obj.summary_text:
                marker_obj.summary_text = summary
                marker_obj.save(update_fields=["summary_text"])

        return Response({"summary": summary}, status=status.HTTP_200_OK)


class ChatAPIView(APIView):
    """
    .POST /api/ai/chat/
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

    @swagger_auto_schema(
        tags=["AI 기능"],
        operation_summary="사용자 챗봇 기능",
        responses={
            200: openapi.Response(
                description="응답 성공", schema=ChatRequestSerializer(many=True)
            )
        },
    )
    def post(self, request, *args, **kwargs):
        serializer = ChatRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        messages = serializer.validated_data["messages"]

        try:
            reply = clova.chat(messages=messages)
        except Exception as e:
            return Response(
                {"error": f"Clova Chat API 호출 실패: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response({"reply": reply}, status=status.HTTP_200_OK)
