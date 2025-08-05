from rest_framework import serializers
from .models import Exercise, PoseStep

class ExerciseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exercise
        fields = '__all__'

class PosestepSerializer(serializers.ModelSerializer):
    class Meta:
        model = PoseStep
        fields = '__all__'
