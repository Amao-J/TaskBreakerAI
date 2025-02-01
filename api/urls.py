from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView,TokenRefreshView
from .views import CreateUserView,LoginView, PreferencesViewSet,DashboardViewSet,logout_view,TeamViewSet,InviteMemberView,AcceptInvitationView
from django.urls import path,include
from .views import forgot_password,reset_password
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register(r'dashboard', DashboardViewSet, basename='dashboard')
router.register(r'onboarding', PreferencesViewSet, basename='preferences')
router.register(r'teams', TeamViewSet, basename='team')



urlpatterns = [
    path('', include(router.urls)),
    
    
    path("logout/", logout_view),
    path('invite/', InviteMemberView.as_view({'post': 'create'}), name='invite-member'),
    path('accept-invite/<uuid:token>/', AcceptInvitationView.as_view(), name='accept-invite'),
    path("user/register/", CreateUserView.as_view(), name='user_register'),
    path("user/login/", LoginView.as_view(), name='user_login'),
    path("token/", TokenObtainPairView.as_view(), name="get_token"),  
    path("token/refresh/", TokenRefreshView.as_view(), name="refresh_token"),
    path("forgotpassword/", forgot_password, name='forgot_password'),
    path("resetpassword/<uidb64>/<token>/", reset_password, name='reset_password'),
]




