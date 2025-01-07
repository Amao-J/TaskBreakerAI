
from django.contrib import admin
from django.urls import path,include
from api import views

urlpatterns = [
  
    path("logout",views.logout_view),
    path('admin/', admin.site.urls),
    path('api/', include(('api.urls', 'core-api'), namespace='core-api')),
    path("api-auth/",include("rest_framework.urls")),
    path("accounts/", include("allauth.urls")),
    path("api/blocksite/",include("blocksite.urls")),
    path("api/taskmanager/",include("task_manager.urls")),
   
    
]
