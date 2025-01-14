from django.urls import path
from .views import create_goal_and_generate_subtasks,calendar_view


urlpatterns=[
     path('generate-subtasks/', create_goal_and_generate_subtasks, name='generate_subtasks'),
     path('calendar/', calendar_view, name='calendar_view'),
     path('subtasks/', views.add_subtask, name='add_subtask'),
    path('subtasks/<int:subtask_id>/', views.edit_subtask, name='edit_subtask')
]