import os
import uuid

import requests
from django.conf import settings


class ClovaClient:
    """
    네이버 Clova Studio Chat-completions API 호출용 클라이언트
    """

    def __init__(self):
        # settings.py에서 불러오기
        self.api_key = settings.CLOVA_API_KEY
        self.base_url = (
            settings.CLOVA_CHAT_COMPLETIONS_URL
        )  # 형식: https://.../chat-completions/{SKILL_ID}

        if (
            not self.api_key
            or "testapp" not in self.base_url
            and "service" not in self.base_url
        ):
            raise RuntimeError("Clova Studio API Key 또는 Base URL 설정을 확인하세요.")

    # 클로바 ai 요약 기능 시스템 룰 설정
    SYSTEM_PROMPT_SUMMARIZE = (
        "너는 여행지 상세 내용을 한국어로 간결하게 요약해 주는 요약 봇이다." "중요한 정보는 놓치지 않으면서 최대한 짧고 쉽게 요약해라."
    )

    # 클로바 ai 챗봇 기능 시스템 룰 설정
    SYSTEM_PROMPT_CHAT = (
        "너는 여행 도우미 봇이다."
        "비속어나 음란물 관련 질문은 “죄송하지만 도와드릴 수 없습니다.” 라고 응답해라."
        "사용자가 초성만 입력하면 “죄송해요, 이해를 못했어요. 조금 더 풀어서 말씀해 주세요.” 라고 추가 질문을 던져라."
        "항상 공손한 어투를 유지해라."
    )

    def _default_headers(self):
        """
        공통 헤더 생성
        X-NCP-CLOVASTUDIO-REQUEST-ID: UUID 로 매 요청마다 생성
        Authorization: Bearer {api_key}
        Content-Type: application/json
        """
        return {
            "Authorization": f"Bearer {self.api_key}",
            "X-NCP-CLOVASTUDIO-REQUEST-ID": str(uuid.uuid4()),
            "Content-Type": "application/json",
        }

    def summarize_text(
        self, text: str, max_tokens: int = 512, temperature: float = 0.5
    ) -> str:
        """
        주어진 긴 텍스트(text)를 간결하게 요약해서 반환.
        Clova Chat-completions API를 '요약 봇' 역할로 호출.
        """
        payload = {
            "model": "HCX-003",
            "messages": [
                {"role": "system", "content": self.SYSTEM_PROMPT_SUMMARIZE},
                {"role": "user", "content": text},
            ],
            "maxTokens": max_tokens,  # camelCase 로 통일
            "temperature": temperature,
        }

        response = requests.post(
            url=self.base_url,
            headers=self._default_headers(),
            json=payload,
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()

        # Clova API가 정상 응답(20000 OK)을 주었는지 확인
        status_code = data.get("status", {}).get("code")
        if status_code != "20000":
            raise ValueError(
                f"Clova 요약 API 호출 실패: status.code = {status_code}, 전체 응답: {data}"
            )

        try:
            # 실제 Clova 요약 텍스트는 result.message.content에 담겨 있음
            summary = data["result"]["message"]["content"]
        except (KeyError, TypeError):
            raise ValueError("Clova 요약 API 응답 구조가 예상과 다릅니다: {}".format(data))

        return summary

    def chat(
        self,
        messages: list[dict[str, str]],
        max_tokens: int = 512,
        temperature: float = 0.8,
    ) -> str:
        payload = {
            "model": "HCX-003",
            "messages": [{"role": "system", "content": self.SYSTEM_PROMPT_CHAT}]
            + messages,
            "maxTokens": max_tokens,
            "temperature": temperature,
        }

        resp = requests.post(
            url=self.base_url,
            headers=self._default_headers(),
            json=payload,
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()

        if data.get("status", {}).get("code") != "20000":
            raise ValueError(f"Clova API 호출 실패: {data}")

        try:
            return data["result"]["message"]["content"]
        except (KeyError, TypeError):
            raise ValueError(f"응답 형식이 예상과 다릅니다: {data}")
