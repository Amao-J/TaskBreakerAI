from rest_framework import serializers
from api.models import Subtasks,Goals
class SubtasksSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subtasks
        fields = ['id', 'description', 'timeframe', 'completed', 'generated_by_ai']


class GoalsSerializer(serializers.ModelSerializer):
    subtasks = SubtasksSerializer(many=True, read_only=True) 

    class Meta:
        model = Goals
        fields = ['id', 'user', 'description', 'completed', 'due_date', 'subtasks']
        