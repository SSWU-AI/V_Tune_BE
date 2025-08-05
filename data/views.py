# data/views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
from data.models import Exercise, PoseStep
from data.serializers import ExerciseSerializer, PosestepSerializer

@api_view(['GET'])
def exercise_list(request):
    queryset = Exercise.objects.all()
    serializer = ExerciseSerializer(queryset, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def exercise_names(request):
    names = list(Exercise.objects.values_list('name', flat=True))
    return Response({"names": names})

@api_view(['GET'])
def exercise_descriptions(request):
    descriptions = list(Exercise.objects.values_list('description', flat=True))
    return Response({"descriptions": descriptions})

@api_view(['GET'])
def exercise_repetitions(request):
    reps = list(Exercise.objects.values_list('repetition', flat=True))
    return Response({"repetitions": reps})

@api_view(['GET'])
def pose_step_list(request):
    queryset = PoseStep.objects.all()
    serializer = PosestepSerializer(queryset, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def posestep_steps(request):
    steps = list(PoseStep.objects.values_list('step_number', flat=True))
    return Response({"step_numbers": steps})

@api_view(['GET'])
def posestep_keypoints(request):
    keypoints = list(PoseStep.objects.values_list('keypoints', flat=True))
    return Response({"keypoints": keypoints})

@api_view(['GET'])
def posestep_descriptions(request):
    descriptions = list(PoseStep.objects.values_list('pose_description', flat=True))
    return Response({"pose_descriptions": descriptions})
