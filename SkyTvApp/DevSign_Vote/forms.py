from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'profile_image']
    
class UserRegisterForm(UserCreationForm):

    role = forms.ChoiceField(choices=User.ROLE_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = User  
        fields = ["email", "password1", "password2", "role"]

class EmailAuthenticationForm(AuthenticationForm):

    username = forms.EmailField(widget=forms.EmailInput(attrs={"class": "form-control"}))