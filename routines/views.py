from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Routine, RoutineExercise, Exercise

class RoutineListView(APIView):
    def get(self, request):
        routines = Routine.objects.all().values('id', 'name', 'description')
        return Response({"routines": list(routines)})

class RoutineDetailView(APIView):
    def get(self, request, routine_id):
        exercises = (
            RoutineExercise.objects
            .filter(routine_id=routine_id)
            .select_related('exercise')
            .order_by('order')
        )

        result = [
            {
                "exercise_id": ex.exercise.id,
                "name": ex.exercise.name,
                "description": ex.exercise.description,
                "repetition": ex.exercise.repetition,
                "order": ex.order
            }
            for ex in exercises
        ]
        return Response({"routine_id": routine_id, "exercises": result})
