from django.urls import path
from .views import create_goal_and_generate_subtasks,calendar_view,add_subtask,edit_subtask,list_goals


urlpatterns=[
     path('generate-subtasks/', create_goal_and_generate_subtasks, name='generate_subtasks'),
     path('calendar/', calendar_view, name='calendar_view'),
     path('addtasks/', add_subtask, name='add_subtask'),
    path('edittask/<int:subtask_id>/', edit_subtask, name='edit_subtask'),
    
    path('list',list_goals,)
]