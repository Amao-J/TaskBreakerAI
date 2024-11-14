from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from .models import User

from rest_framework_simplejwt.tokens import RefreshToken


from allauth.account.adapter import DefaultAccountAdapter
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User

class CustomAccountAdapter(DefaultAccountAdapter):
    def save_user(self, request, user, form=None, commit=True):
        
        if form is None:
            return None
        
        
        data = form.cleaned_data if hasattr(form, 'cleaned_data') else form
        user.email = data.get('email')
        user.first_name = data.get('first_name', '')
        user.last_name = data.get('last_name', '')
        user.username = data.get('username', user.email)
        user.set_password(data.get('password1', ''))

        # Save user before proceeding with related models
        user.save()

        # Generate JWT tokens after user creation
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        return {
            'user': user,
            'refresh': str(refresh),
            'access': access_token,
        }



class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
       
        if sociallogin.is_existing:
            return
        
        email = sociallogin.account.extra_data.get('email')
        if email:
            try:
                user = User.objects.get(email=email)
                sociallogin.connect(request, user)
            except User.DoesNotExist:
                pass
   
    def save_user(self, request, sociallogin, form=None):
      
        user = sociallogin.user
        extra_data = sociallogin.account.extra_data
        
        user.email = extra_data.get('email')
        user.first_name = extra_data.get('given_name', '')
        user.last_name = extra_data.get('family_name', '')
        user.username = extra_data.get('email')

        user.save()
        return user
