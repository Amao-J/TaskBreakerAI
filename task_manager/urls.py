from django.urls import path
from .views import create_goal_and_generate_subtasks


urlpatterns=[
     path('generate-subtasks/', create_goal_and_generate_subtasks, name='generate_subtasks'),
]