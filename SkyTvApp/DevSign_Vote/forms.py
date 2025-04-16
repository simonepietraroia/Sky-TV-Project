from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User, Session, HealthCard

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

class VotingSessionForm(forms.ModelForm):
    session_name = forms.CharField(
        label="Session Name",
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    start_time = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'})
    )
    end_time = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'})
    )
    health_cards = forms.ModelMultipleChoiceField(
        queryset=HealthCard.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True
    )

    class Meta:
        model = Session
        fields = ['start_time', 'end_time']