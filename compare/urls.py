from django.urls import path
from .views import compare_pose

urlpatterns = [
    path('', compare_pose, name='compare-pose'),
]