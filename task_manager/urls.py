from django.urls import path
from .views import CreateGoalView


urlpatterns=[
    path('create-goal/', CreateGoalView.as_view(), name='create_goal'),
]