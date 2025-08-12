from django.db import models

class Exercise(models.Model):
    name = models.TextField(null=False)
    description = models.TextField(blank=True, null=True)
    repetition = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = "Exercise"  # ✅ 실제 SQLite 테이블명 지정

class PoseStep(models.Model):
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE, db_column="exercise_id")
    step_number = models.IntegerField()
    keypoints = models.TextField(blank=True, null=True)
    pose_description = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "PoseStep"  # ✅ 실제 SQLite 테이블명 지정
