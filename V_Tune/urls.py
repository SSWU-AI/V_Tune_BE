from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.http import HttpResponse 

schema_view = get_schema_view(
   openapi.Info(
      title="V-Tune API",
      default_version='v1',
      description="V-Tune API 문서입니다.",
   ),
   public=True,
   permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    # 기본 경로에서 텍스트 응답
    path('', lambda request: HttpResponse("배포가 완료되었습니다. /swagger/ 에서 API 문서를 확인하세요.")),

    path('admin/', admin.site.urls),
    path('api/data/', include('data.urls')), 
    path('api/feedback/', include('feedback.urls')),
    path('api/compare/', include('compare.urls')),
    path('api/tts/', include('tts.urls')),
    path('api/routines/', include('routines.urls')),

    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
