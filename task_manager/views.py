from django.shortcuts import render
from api.models import Goals,Subtasks
from .serializers import GoalsSerializer
from rest_framework import generics
from rest_framework.response import Response

class CreateGoalView(generics.CreateAPIView):
    queryset = Goals.objects.all()
    serializer_class = GoalsSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        goal = serializer.save()  


        #subtasks = process_goal(goal.description)

       
        # for task in subtasks:
        #     Subtasks.objects.create(goal=goal, description=task)

        return Response(serializer.data, status=status.HTTP_201_CREATED)