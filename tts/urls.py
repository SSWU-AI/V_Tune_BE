from django.urls import path
from .views import tts_api

urlpatterns = [
    path('', tts_api),  # 빈 path: /api/tts/ 에 대응
]
