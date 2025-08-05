# data/serializers.py

from rest_framework import serializers
from .models import Exercise, PoseStep

class ExerciseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exercise
        fields = '__all__'

class PoseStepSerializer(serializers.ModelSerializer):  # ✅ 대문자 S로 수정
    class Meta:
        model = PoseStep
        fields = '__all__'
