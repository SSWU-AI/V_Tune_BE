from rest_framework.decorators import api_view
from rest_framework.response import Response
from data.models import Exercise, PoseStep
from data.serializers import ExerciseSerializer, PoseStepSerializer

# ✅ Exercise 공통 필터
def filter_exercise_queryset(request):
    queryset = Exercise.objects.all()
    name = request.GET.get('name')
    description = request.GET.get('description')
    repetition = request.GET.get('repetition')

    if name:
        queryset = queryset.filter(name__icontains=name)
    if description:
        queryset = queryset.filter(description__icontains=description)
    if repetition:
        queryset = queryset.filter(repetition=repetition)

    return queryset

# ✅ PoseStep 공통 필터
def filter_pose_queryset(request):
    queryset = PoseStep.objects.all()
    exercise_id = request.GET.get('exercise_id')
    step_number = request.GET.get('step_number')
    pose_description = request.GET.get('pose_description')

    if exercise_id:
        queryset = queryset.filter(exercise_id=exercise_id)
    if step_number:
        queryset = queryset.filter(step_number=step_number)
    if pose_description:
        queryset = queryset.filter(pose_description__icontains=pose_description)

    return queryset

# -------------------------------
# ✅ Exercise 관련 API
# -------------------------------
@api_view(['GET'])
def exercise_list(request):
    queryset = filter_exercise_queryset(request)
    serializer = ExerciseSerializer(queryset, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def exercise_names(request):
    queryset = filter_exercise_queryset(request)
    names = list(queryset.values_list('name', flat=True))
    return Response({"names": names})

@api_view(['GET'])
def exercise_descriptions(request):
    queryset = filter_exercise_queryset(request)
    descriptions = list(queryset.values_list('description', flat=True))
    return Response({"descriptions": descriptions})

@api_view(['GET'])
def exercise_repetitions(request):
    queryset = filter_exercise_queryset(request)
    reps = list(queryset.values_list('repetition', flat=True))
    return Response({"repetitions": reps})

# -------------------------------
# ✅ PoseStep 관련 API
# -------------------------------
@api_view(['GET'])
def pose_step_list(request):
    queryset = filter_pose_queryset(request)
    serializer = PoseStepSerializer(queryset, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def posestep_steps(request):
    queryset = filter_pose_queryset(request)
    steps = list(queryset.values_list('step_number', flat=True))
    return Response({"step_numbers": steps})

@api_view(['GET'])
def posestep_keypoints(request):
    queryset = filter_pose_queryset(request)
    keypoints = list(queryset.values_list('keypoints', flat=True))
    return Response({"keypoints": keypoints})

@api_view(['GET'])
def posestep_descriptions(request):
    queryset = filter_pose_queryset(request)
    descriptions = list(queryset.values_list('pose_description', flat=True))
    return Response({"pose_descriptions": descriptions})
