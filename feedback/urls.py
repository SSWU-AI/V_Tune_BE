from django.urls import path
from .views import feedback_api

urlpatterns = [
    path('', feedback_api),  # 빈 path: /api/feedback/ 에 대응
]
