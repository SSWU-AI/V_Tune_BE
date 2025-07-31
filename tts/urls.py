from django.urls import path
from .views import tts_view

urlpatterns = [
    path('', tts_view),  # /tts/로 POST 요청 보내면 이 함수 실행됨
]
