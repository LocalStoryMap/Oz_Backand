from django.urls import path
from .views import SummarizeAPIView, ChatAPIView

urlpatterns = [
    path('summarize/', SummarizeAPIView.as_view(), name='api-summarize'),
    path('chat/', ChatAPIView.as_view(), name='api-chat'),
]
