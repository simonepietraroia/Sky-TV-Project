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
    session_name = forms.CharField(
        label="Session Name",
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    start_time = forms.DateTimeField(
        label="Start Time",
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'})
    )
    end_time = forms.DateTimeField(
        label="End Time",
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
        required=False
    )
    health_cards = forms.ModelMultipleChoiceField(
        queryset=HealthCard.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Select Health Cards"
    )

    class Meta:
        model  = Session
        # include your new session_name + the m2m field:
        fields = [
            'session_name',
            'start_time',
            'end_time',
            'health_cards',
        ]

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