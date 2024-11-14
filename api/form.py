from allauth.account.forms import SignupForm
from django import forms
from .models import BlockedSite

class CustomSignupForm(SignupForm):
    first_name = forms.CharField(max_length=30, label='First Name')
    last_name = forms.CharField(max_length=30, label='Last Name')
    def signup(self, request, user):
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.save()
        return user
    
    
    



class BlockedSiteForm(forms.ModelForm):
    class Meta:
        model = BlockedSite
        fields = ['url', 'redirect_url']
