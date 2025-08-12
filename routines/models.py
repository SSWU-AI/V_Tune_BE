from django.db import models

class Exercise(models.Model):
    name = models.TextField()
    description = models.TextField(blank=True, null=True)
    repetition = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Exercise'

class Routine(models.Model):
    name = models.TextField()
    description = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Routine'

class RoutineExercise(models.Model):
    routine = models.ForeignKey(Routine, models.DO_NOTHING, db_column='routine_id')
    exercise = models.ForeignKey(Exercise, models.DO_NOTHING, db_column='exercise_id')
    order = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'RoutineExercise'
