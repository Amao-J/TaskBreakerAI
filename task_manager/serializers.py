from rest_framework import serializers
from api.models import Subtasks,Goals
from rest_framework import serializers
from .models import Subtasks

class SubtaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subtasks
        fields = ['id', 'goal', 'description', 'completed', 'end_time', 'created_at', 'completed_at']
        read_only_fields = ['id', 'created_at', 'completed_at']


class GoalsSerializer(serializers.ModelSerializer):
    subtasks = SubtasksSerializer(many=True, read_only=True) 

    class Meta:
        model = Goals
        fields = ['id', 'user', 'description', 'completed', 'due_date', 'subtasks']
        