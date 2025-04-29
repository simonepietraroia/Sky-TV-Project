from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate  
from django.contrib.auth.forms import AuthenticationForm
from .forms import UserRegisterForm, ProfileUpdateForm, EmailAuthenticationForm, VotingSessionForm
import base64
from django.core.files.base import ContentFile
from django.views.decorators.csrf import csrf_exempt
from .models import Session, HealthCard, Department, Team, Vote
# AggregateVotesTable, TrendAnalysis
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.contrib import messages
from django.http import HttpResponse, HttpResponseBadRequest
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404



def homepage(request):
    return render(request, 'DevSign_Vote/home.html')

@login_required
def profile(request):
    return render(request, "DevSign_Vote/profile.html")

@csrf_exempt
@login_required
def edit_profile(request):
    user = request.user
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = ProfileUpdateForm(instance=user)

    departments = Department.objects.all()
    teams = Team.objects.filter(DepartmentID=user.TeamID.DepartmentID) if user.TeamID else Team.objects.none()

    return render(request, 'DevSign_Vote/edit_profile.html', {
        'form': form,
        'departments': departments,
        'teams': teams,
    })


@login_required
def portal_view(request, session_id):
    user = request.user
    context = {'user': user}

    if user.role == "team_leader":
        context['team_sessions'] = Session.objects.filter(UserID=user)

    elif user.role == "department_leader":
        teams = Team.objects.filter(DepartmentID=user.TeamID.DepartmentID)
        context['department_summary'] = AggregateVotesTable.objects.filter(TeamID__in=teams)
        context['department_trends'] = TrendAnalysis.objects.filter(TeamID__in=teams)

    elif user.role == "senior_engineer":
        context['company_summary'] = AggregateVotesTable.objects.all()
        context['company_trends'] = TrendAnalysis.objects.all()

    return render(request, 'DevSign_Vote/portal.html', context)

@login_required
@csrf_exempt
def create_voting_session(request):
    if not request.user.is_team_leader():
        messages.error(request, "Only team leaders can create sessions.")
        return redirect('home')

    if request.method == 'POST':
        form = VotingSessionForm(request.POST)
        if form.is_valid():
            session = form.save(commit=False)
            session.UserID = request.user
            session.Status = "Open"
            session.save()
            form.save_m2m()

            messages.success(request, "Session created successfully!")
            return redirect('session-select')
    else:
        form = VotingSessionForm()

    return render(request, 'DevSign_Vote/create_session.html', {'form': form})

@csrf_exempt
def signup(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False) 
            user.role = form.cleaned_data['role']  
            user.save()  
            return redirect('login')  
    else:
        form = UserRegisterForm()

    return render(request, "DevSign_Vote/signup.html", {"form": form})

@csrf_exempt
def user_login(request):
    if request.method == "POST":
        form = EmailAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get("username") 
            password = form.cleaned_data.get("password")
            user = authenticate(email=email, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, "Welcome back!")
                return redirect("home")
            else:
                messages.error(request, "Invalid email or password.")
        else:
            messages.error(request, "Invalid credentials.")
    else:
        form = EmailAuthenticationForm()

    return render(request, "DevSign_Vote/login.html", {"form": form})

def user_logout(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect("home")

@login_required
def profile(request):
    user = request.user
    profile_image_base64 = None

    if user.profile_image:  
        try:
            image_bytes = user.profile_image.read()  
            profile_image_base64 = base64.b64encode(image_bytes).decode("utf-8")  
        except Exception as e:
            print(f"Error encoding image: {e}") 

    return render(request, "DevSign_Vote/profile.html", {"user": user, "profile_image_base64": profile_image_base64})


def dashboard_view(request):
    user = request.user
    team_sessions = VotingSession.objects.filter(team_leader=user)
    department_summary = TeamSummary.objects.filter(department_leader=user)
    company_summary = DepartmentSummary.objects.all()

    context = {
        'user': user,
        'team_sessions': team_sessions,
        'department_summary': department_summary,
        'company_summary': company_summary,
    }
    return render(request, 'DevSign_Vote/dashboard.html', context)

@login_required
@csrf_exempt
def vote_on_session(request, session_id):
    session = Session.objects.get(pk=session_id)

    if session.Status == "Closed" or session.EndTime < timezone.now():
        messages.error(request, "This session is closed.")
        return redirect("portal")

    health_cards = HealthCard.objects.all()

    if request.method == "POST":
        for card in health_cards:
            vote_value = request.POST.get(f"vote_{card.CardID}")
            progress = request.POST.get(f"trend_{card.CardID}")
            comment = request.POST.get(f"comment_{card.CardID}")

            if vote_value and progress:
                Vote.objects.create(
                    TeamID=request.user.TeamID,
                    UserID=request.user,
                    CardID=card,
                    SessionID=session,
                    VoteValue=vote_value,
                    Progress=progress,
                    Comment=comment
                )
        messages.success(request, "Your votes have been submitted.")
        return redirect("portal")

    return render(request, "DevSign_Vote/vote_session.html", {
        "session": session,
        "cards": health_cards
    })

@login_required(login_url='login')  
def session_select(request):
    now = timezone.now()
    sessions = Session.objects.filter(Status="Open", EndTime__gt=now)

    department_id = request.GET.get('department')
    team_id = request.GET.get('team')

    if department_id:
        sessions = sessions.filter(DepartmentID=department_id)
    if team_id:
        sessions = sessions.filter(TeamID=team_id)

    departments = Department.objects.all()
    teams = Team.objects.all()

    return render(request, 'DevSign_Vote/session-select.html', {
        'sessions': sessions,
        'departments': departments,
        'teams': teams,
    })

@csrf_exempt
@login_required
def join_session(request, session_id):
    session = get_object_or_404(Session, pk=session_id)
    cards = session.health_cards.all()

    if request.method == 'POST':
        if not request.user.TeamID:
            messages.error(request, "You must belong to a team to submit votes.")
            return redirect('session-select')

        for card in cards:
            vote_value = request.POST.get(f'vote_{card.CardID}')
            progress = request.POST.get(f'trend_{card.CardID}')
            comment = request.POST.get(f'comment_{card.CardID}')

            if vote_value and progress:
                Vote.objects.create(
                    TeamID=request.user.TeamID,
                    UserID=request.user,
                    CardID=card,
                    SessionID=session,
                    VoteValue=vote_value,
                    Progress=progress,
                    Comment=comment
                )

        messages.success(request, "Your votes have been submitted successfully!")
        return redirect('/')  # or wherever you want

    return render(request, 'DevSign_Vote/voting.html', {
        'session': session,
        'cards': cards,
    })
