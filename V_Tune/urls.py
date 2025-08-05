# V_Tune/urls.py

from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from django.conf import settings
from django.conf.urls.static import static  

def home(request):
    return HttpResponse("성공적으로 배포되었습니다")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/feedback/', include('feedback.urls')),
    path('api/tts/', include('tts.urls')),
    path('api/data/', include('data.urls')),
    path('api/compare/', include('compare.urls')),
    path('', home),
]

# 개발 서버에서 정적 파일 서빙
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
