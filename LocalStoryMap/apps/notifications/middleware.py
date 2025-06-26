from urllib.parse import parse_qs

import jwt
from channels.middleware import BaseMiddleware
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser


class JWTAuthMiddleware(BaseMiddleware):
    """
    WebSocket 연결시 'Authorization: Bearer <token>' 헤더나
    '?token=<token>' 쿼리 파라미터로 들어온 JWT를 검증해
    scope['user'] 에 User 인스턴스를 설정합니다.
    """

    async def __call__(self, scope, receive, send):
        # 1) 헤더에서 토큰 찾기
        headers = dict(scope.get("headers", []))
        raw_token = None
        auth = headers.get(b"authorization")
        if auth:
            parts = auth.decode().split()
            if len(parts) == 2 and parts[0].lower() == "bearer":
                raw_token = parts[1]

        # 2) 없으면 쿼리스트링에서 찾기
        if not raw_token:
            qs = parse_qs(scope.get("query_string", b"").decode())
            token_list = qs.get("token") or qs.get("access")
            if token_list:
                raw_token = token_list[0]

        # 3) 토큰 검증
        if raw_token:
            try:
                # settings.SECRET_KEY 로 HS256 디코딩
                payload = jwt.decode(
                    raw_token, settings.SECRET_KEY, algorithms=["HS256"]
                )
                user = await get_user_model().objects.aget(id=payload.get("user_id"))
                scope["user"] = user
            except Exception:
                scope["user"] = AnonymousUser()
        else:
            scope["user"] = AnonymousUser()

        return await super().__call__(scope, receive, send)
