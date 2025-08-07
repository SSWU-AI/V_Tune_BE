from django.urls import path
from .views import RoutineListView, RoutineDetailView

urlpatterns = [
    path('list/', RoutineListView.as_view(), name='routine-list'),
    path('<int:routine_id>/exercises/', RoutineDetailView.as_view(), name='routine-detail'),
]
