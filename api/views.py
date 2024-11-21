from django.shortcuts import render, redirect,HttpResponse
from rest_framework_simplejwt.tokens import RefreshToken
from django.http import JsonResponse
from rest_framework.decorators import api_view,permission_classes
from rest_framework.permissions import AllowAny
from django.contrib.auth import login, logout
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status, generics
from .models import User,BlockedSite,Dashboard,Preferences
from .serializers import UserSerializer,PreferencesSerializer
from blocksite.serializers import BlockedSiteSerializer
from django.utils.http import urlsafe_base64_decode
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status,permissions,viewsets
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from rest_framework.decorators import action




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

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            return JsonResponse({
                "message": "Login successful",
                "user_id": user.id,
                "access": access_token,
                "refresh": str(refresh)
            }, status=status.HTTP_200_OK)
        else:
            return JsonResponse({"error": "Invalid email or password"}, status=status.HTTP_400_BAD_REQUEST)

         


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
            blocked_sites = BlockedSite.objects.filter(user=user)

            response_data = {
                "total_blocked_sites": blocked_sites.count(),
                "completed_percentage": dashboard.calculate_completed_percentage(),
                "sites": BlockedSiteSerializer(blocked_sites, many=True).data,
                "missed_or_overdue_goals": list(dashboard.missed_or_overdue_goals()),
                "overdue_tasks_by_goals": self.format_overdue_tasks(dashboard),
                "tasks_completed_day": dashboard.tasks_completed(period='day'),
                "tasks_completed_week": dashboard.tasks_completed(period='week'),
                "task_completion_rate": dashboard.task_completion_rate(),
                "top_productivity_hours":dashboard.top_productivity_hours()
            }

            return Response(response_data, status=status.HTTP_200_OK)
        except Dashboard.DoesNotExist:
            return Response({"error": "Dashboard not found."}, status=status.HTTP_404_NOT_FOUND)

    def format_overdue_tasks(self, dashboard):
        return {
            goal.description: [
                {"task": subtask.description, "due_date": goal.due_date.isoformat()}
                for subtask in subtasks
            ]
            for goal, subtasks in dashboard.overdue_tasks_grouped_by_goals().items()
        }

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
        
        # Perform the deletion
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



