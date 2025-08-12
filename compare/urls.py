from django.urls import path
from .views import compare_and_feedback

urlpatterns = [
    path('', compare_and_feedback, name='compare-and-feedback'),
]
