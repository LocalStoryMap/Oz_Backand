from humps.main import camelize
from rest_framework.renderers import JSONRenderer


class CamelCaseJSONRenderer(JSONRenderer):
    """
    DRF가 반환하는 JSON 응답의 key를 pyhumps.camelize() 로 snake_case → camelCase 로 변환합니다.
    """

    def render(self, data, accepted_media_type=None, renderer_context=None):
        # data가 dict나 list가 아니면, 기본 JSONRenderer 작업을 그대로 수행
        if data is None or not isinstance(data, (dict, list)):
            return super().render(data, accepted_media_type, renderer_context)

        # pyhumps.camelize() 로 중첩된 딕셔너리/리스트 내부의 모든 키를 camelCase로 변환
        camelized = camelize(data)
        return super().render(camelized, accepted_media_type, renderer_context)
