from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User, Session, HealthCard, Vote
from django.forms import Select

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'role', 'DepartmentID', 'TeamID']

class UserRegisterForm(UserCreationForm):

    role = forms.ChoiceField(choices=User.ROLE_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = User  
        fields = ["email", "password1", "password2", "role"]

class EmailAuthenticationForm(AuthenticationForm):

    username = forms.EmailField(widget=forms.EmailInput(attrs={"class": "form-control"}))

class VotingSessionForm(forms.ModelForm):
    class Meta:
        model = Session
        fields = ['session_name', 'StartTime', 'EndTime', 'health_cards']

        widgets = {
            'session_name': forms.TextInput(attrs={'class': 'form-control'}),
            'StartTime': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'EndTime': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'health_cards': forms.CheckboxSelectMultiple()
        }
        
class VoteForm(forms.ModelForm):
    VOTE_CHOICES = [
        (1, '🔴 Red'), (2, '🟡 Yellow'), (3, '🟢 Green')
    ]
    TREND_CHOICES = [
        ('up', '⬆️ Trending Up'), ('down', '⬇️ Trending Down')
    ]

    VoteValue = forms.ChoiceField(choices=VOTE_CHOICES, widget=forms.RadioSelect)
    Progress = forms.ChoiceField(choices=TREND_CHOICES, widget=forms.RadioSelect)
    Comment = forms.CharField(widget=forms.Textarea(attrs={'rows': 2}), required=False)

    class Meta:
        model = Vote
        fields = ['VoteValue', 'Progress', 'Comment']