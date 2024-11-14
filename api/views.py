from django.shortcuts import render, redirect,HttpResponse
from rest_framework_simplejwt.tokens import RefreshToken
from django.http import JsonResponse
from django.contrib.auth import login, logout,get_backends
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status, generics
from .models import User,BlockedSite,Dashboard
from .serializers import UserSerializer
from blocksite.serializers import BlockedSiteSerializer
from django.views.decorators.csrf import csrf_exempt
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
        blocked_sites = BlockedSite.objects.filter(user=user)
        dashboard = Dashboard.objects.get(user=request.user)
        
        data = {
            "total_blocked_sites": blocked_sites.count(),
            'completed_percentage': dashboard.completed_percentage(),
            "sites": BlockedSiteSerializer(blocked_sites, many=True).data,
            "missed_or_overdue_tasks":dashboard.missed_or_overdue_tasks(),
            "tasks_completed_day": dashboard.tasks_completed(period='day'),
            "tasks_completed_week": dashboard.tasks_completed(period='week'),
            "task_completion_rate": dashboard.task_completion_rate(),
            
        }
        return Response(data)

    
    
@csrf_exempt
def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        user = User.objects.filter(email=email).first()
        
        if not user:
            return JsonResponse({'error':'Email not found'})
        
        if user:
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            reset_link = f"{request.build_absolute_uri('/api/resetpassword/')}{uid}/{token}/"
            
        
            subject = "Password Reset Requested"
            message = render_to_string('email_template.html', {'reset_link': reset_link})
            send_mail(subject, message, 'yourapp@example.com', [email])
            
            return JsonResponse({
                "message": "A link was sent to your email",
                
            
            }, status=status.HTTP_200_OK)
    
    return render(request, 'forgot_password.html')


def reset_password(request, uidb64, token):
    try:
        # Decode the user ID from the URL
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')

            if new_password == confirm_password:
                user.set_password(new_password)
                user.save()
                
                backend = get_backends()[0]  # Choose the correct backend from the list
                login(request, user, backend=backend.__module__ + '.' + backend.__class__.__name__)

                return JsonResponse({
                "message": "Your password was successfully reset. You are now logged in",
                
            
            }, status=status.HTTP_200_OK)
            else:
                return JsonResponse({
                "message": "Passwords do not match. Please try again.",
                
            
            })

        return render(request, 'reset_password.html', {'valid_link': True})
    else:
        return HttpResponse("The password reset link is invalid or has expired.")


