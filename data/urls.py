from django.urls import path
from .views import (
    exercise_list,
    exercise_names,
    exercise_descriptions,
    exercise_repetitions,
    pose_step_list,
    posestep_steps,
    posestep_keypoints,
    posestep_descriptions
)

urlpatterns = [
    path('exercises/', exercise_list),
    path('exercises/names/', exercise_names),
    path('exercises/descriptions/', exercise_descriptions),
    path('exercises/repetitions/', exercise_repetitions),
    path('pose-steps/', pose_step_list),
    path('pose-steps/steps/', posestep_steps),
    path('pose-steps/keypoints/', posestep_keypoints),
    path('pose-steps/descriptions/', posestep_descriptions),
]
