from django.shortcuts import redirect,get_object_or_404
from rest_framework_simplejwt.tokens import RefreshToken
from django.http import JsonResponse
from rest_framework.decorators import api_view,permission_classes,action
from django.contrib.auth import login, logout
from .models import User,BlockedSite,Dashboard,Preferences,Team,Invitation
from .serializers import UserSerializer,PreferencesSerializer,GoalSerializer, SubtaskSerializer,InvitationSerializer,TeamSerializer
from blocksite.serializers import BlockedSiteSerializer
from django.utils.http import urlsafe_base64_decode
from django.shortcuts import redirect
from django.contrib.auth import authenticate, login
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny,BasePermission,IsAuthenticated
from rest_framework.response import Response
from rest_framework import status,permissions,viewsets,generics
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.shortcuts import get_object_or_404
import django.utils.timezone as timezone
from rest_framework.throttling import AnonRateThrottle
from django.conf import settings
import logging


logger = logging.getLogger(__name__)

class CreateUserView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        return Response({
            "user": serializer.data,
            "refresh": str(refresh),
            "access": access_token,
        }, status=status.HTTP_201_CREATED)
        
        
        



class LoginView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [AnonRateThrottle]

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        if not email or not password:
            return Response({
                "error": "Missing email or password",
                "message": "Both email and password are required."
            }, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(request, email=email, password=password)

        if user is None:
            logger.warning(f"Login failed for email: {email}")
            return Response({
                "error": "Invalid email or password",
                "message": "Wrong credentials provided."
            }, status=status.HTTP_400_BAD_REQUEST)

        login(request, user)
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        logger.info(f"Login successful for user {user.email} (ID: {user.id})")
        return Response({
            "message": "Login successful",
            "user_id": user.id,
            "access": access_token,
            "refresh": str(refresh)
        }, status=status.HTTP_200_OK)
         



def logout_view(request):
    logout(request)
    return redirect("/")



class DashboardViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['get'])
    def overview(self, request):
        user = request.user
       
        try:
            dashboard = Dashboard.objects.get(user=user)
            if not dashboard:
                return Response({"error": "Dashboard not found."}, status=status.HTTP_404_NOT_FOUND)
             
            blocked_sites = BlockedSite.objects.filter(user=user)

            
            goals = GoalSerializer(dashboard.goals.all(), many=True).data
            subtasks = SubtaskSerializer(dashboard.subtasks.all(), many=True).data
           

            response_data = {
                "user":user.first_name,
                "total_blocked_sites": blocked_sites.count(),
                "completed_percentage": dashboard.calculate_completed_percentage(),
                "sites": BlockedSiteSerializer(blocked_sites, many=True).data,
                "missed_or_overdue_goals": goals,  
                "overdue_tasks_by_goals": self.format_overdue_tasks(dashboard),
                "tasks_completed_day": dashboard.tasks_completed(period='day'),
                "tasks_completed_week": dashboard.tasks_completed(period='week'),
                "task_completion_rate": dashboard.task_completion_rate(),
                "top_productivity_hours":dashboard.top_productivity_hours(),
                "total_subtasks":dashboard.subtasks.count(),
                "goals": goals,
                "subtasks": subtasks,
            
            }

            return Response({"data": response_data}, status=status.HTTP_200_OK)
        except Dashboard.DoesNotExist:
            return Response({"error": "Dashboard not found."}, status=status.HTTP_404_NOT_FOUND)
        
        
    
    def format_overdue_tasks(self, dashboard):
        overdue_tasks = {}
        for goal in dashboard.missed_or_overdue_goals():
            overdue_tasks[goal.description] = [
                {"task": subtask.description, "due_date": subtask.end_time.isoformat()}
                for subtask in goal.tasks.filter(end_time__lt=timezone.now(), completed=False)
            ]
        return overdue_tasks


class PreferencesViewSet(viewsets.ModelViewSet):
    queryset = Preferences.objects.all()
    serializer_class = PreferencesSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Preferences.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['post'])
    def add_preference(self, request):
        data = request.data
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response(
            {"message": "Preference added successfully"},
            status=status.HTTP_201_CREATED
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.user != request.user:
            return Response(
                {"detail": "You do not have permission to delete this preference."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        
        self.perform_destroy(instance)
        return Response(
            {"message": "Preference deleted successfully."},
            status=status.HTTP_204_NO_CONTENT
        )

    

    
    
@api_view(['POST'])
@permission_classes([AllowAny])
def forgot_password(request):
    email = request.data.get('email')
    user = User.objects.filter(email=email).first()
    
    if not user:
        return Response({'error': 'Email not found'}, status=status.HTTP_404_NOT_FOUND)

    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    reset_link = f"{request.build_absolute_uri('/api/resetpassword/')}{uid}/{token}/"

    subject = "Password Reset Requested"
    message = render_to_string('email_template.html', {'reset_link': reset_link})
    send_mail(subject, message, 'yourapp@example.com', [email])

    return Response({"message": "A password reset link has been sent to your email."}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def reset_password(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        return Response({"error": "Invalid or expired reset link."}, status=status.HTTP_400_BAD_REQUEST)

    if not default_token_generator.check_token(user, token):
        return Response({"error": "Invalid or expired reset link."}, status=status.HTTP_400_BAD_REQUEST)

    new_password = request.data.get('new_password')
    confirm_password = request.data.get('confirm_password')

    if new_password != confirm_password:
        return Response({"error": "Passwords do not match."}, status=status.HTTP_400_BAD_REQUEST)

    user.set_password(new_password)
    user.save()

    return Response({"message": "Password reset successful."}, status=status.HTTP_200_OK)



class TeamViewSet(viewsets.ModelViewSet):
    serializer_class = TeamSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Team.objects.filter(members=self.request.user) | Team.objects.filter(creator=self.request.user)

    def perform_create(self, serializer):
        team = serializer.save(creator=self.request.user)
        team.members.add(self.request.user)

    def perform_destroy(self, instance):
        if instance.creator != self.request.user:
            return Response({"message":"Only the team creator can delete the team."})
        instance.delete()
        


class IsTeamCreator(BasePermission):
    def has_permission(self, request, view):
        team_id = request.data.get("team_id")
        return request.user.teams.filter(id=team_id, creator=request.user).exists()

class InviteMemberView(viewsets.ViewSet):
    
    permission_classes = [IsAuthenticated, IsTeamCreator]
    
    def create(self, request):
        email = request.data.get('email')
        team_id = request.data.get('team_id')
        role = request.data.get('role')

       
        invitation = Invitation.objects.create(email=email, team_id=team_id, role=role)

        invite_link = f"{settings.FRONTEND_URL}/accept-invite/{invitation.token}"
        send_mail(
            "You're invited to a team!",
            f"Click here to accept the invite: {invite_link}",
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )

        return Response({"message": "Invitation sent successfully"}, status=status.HTTP_201_CREATED)
    
    



class AcceptInvitationView(APIView):
    def post(self, request, token):
        invitation = get_object_or_404(Invitation, token=token, accepted=False)
        user = request.user  

        
        invitation.team.members.add(user)
        invitation.accepted = True
        invitation.save()

        return Response({"message": "Invitation accepted"}, status=status.HTTP_200_OK)
