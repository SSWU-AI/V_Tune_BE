from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

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
    path('admin/', admin.site.urls),
    path('api/data/', include('data.urls')),  # 너가 만든 data urls 연결
    path('api/feedback/', include('feedback.urls')),
    path('api/compare/', include('compare.urls')),
    path('api/tts/', include('tts.urls')),

    # ✅ Swagger 문서 URL 추가
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

]
