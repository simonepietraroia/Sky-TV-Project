from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from collections import defaultdict
from django.db.models import Count, Q

from .forms import UserRegisterForm, ProfileUpdateForm, EmailAuthenticationForm, VotingSessionForm
from .models import Session, HealthCard, Department, Team, Vote

import base64
import json

def homepage(request):
    return render(request, 'DevSign_Vote/home.html')


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
                if user.role == "engineer":
                    return redirect("session-select")
                elif user.role == "team_leader":
                    return redirect("session-select")
                else:
                    return redirect("portal")
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
        except Exception:
            pass
    return render(request, "DevSign_Vote/profile.html", {
        "user": user,
        "profile_image_base64": profile_image_base64
    })


@csrf_exempt
@login_required
def edit_profile(request):
    user = request.user
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            if user.role == "engineer":
                return redirect("session-select")
            elif user.role == "team_leader":
                return redirect("create_session")
            else:
                return redirect("portal")
    else:
        form = ProfileUpdateForm(instance=user)

    departments = Department.objects.all()
    teams = Team.objects.filter(DepartmentID=user.TeamID.DepartmentID) if user.TeamID else Team.objects.none()

    profile_image_base64 = None
    if user.profile_image and hasattr(user.profile_image, 'read'):
        try:
            image_bytes = user.profile_image.read()
            profile_image_base64 = base64.b64encode(image_bytes).decode("utf-8")
            user.profile_image.seek(0)
        except Exception:
            pass

    return render(request, 'DevSign_Vote/edit_profile.html', {
        'form': form,
        'departments': departments,
        'teams': teams,
        'profile_image_base64': profile_image_base64,
    })


@login_required
@csrf_exempt
def create_voting_session(request):
    if not request.user.is_team_leader():
        messages.error(request, "Only team leaders can create sessions.")
        return redirect("home")

    if request.method == "POST":
        form = VotingSessionForm(request.POST)
        if form.is_valid():
            session = form.save(commit=False)
            session.UserID = request.user
            session.Status = "Open"
            session.save()
            form.save_m2m()
            messages.success(request, "Session created successfully.")
            return redirect("session-select")
    else:
        form = VotingSessionForm()
    return render(request, "DevSign_Vote/create_session.html", {"form": form})


@login_required
@csrf_exempt
def vote_on_session(request, session_id):
    session = get_object_or_404(Session, pk=session_id)

    if request.user.role != "engineer":
        messages.error(request, "Only engineers can vote.")
        return redirect("home")

    if session.Status == "Closed" or session.EndTime < timezone.now():
        messages.error(request, "Voting is closed for this session.")
        return redirect("session-select")

    health_cards = HealthCard.objects.all()

    if request.method == "POST":
        for card in health_cards:
            vote_value = request.POST.get(f"vote_{card.CardID}")
            trend = request.POST.get(f"trend_{card.CardID}")
            comment = request.POST.get(f"comment_{card.CardID}")
            if vote_value and trend:
                Vote.objects.create(
                    TeamID=request.user.TeamID,
                    UserID=request.user,
                    CardID=card,
                    SessionID=session,
                    VoteValue=vote_value,
                    Progress=trend,
                    Comment=comment
                )
        messages.success(request, "Your votes have been submitted.")
        return redirect("confirmation", session_id=session.SessionID)

    return render(request, "DevSign_Vote/vote_session.html", {
        "session": session,
        "cards": health_cards
    })


@login_required
def session_select(request):
    now = timezone.now()
    sessions = Session.objects.filter(Status="Open", EndTime__gt=now)

    department_id = request.GET.get('department')
    team_id = request.GET.get('team')

    if department_id:
        sessions = sessions.filter(DepartmentID=department_id)
    if team_id:
        sessions = sessions.filter(TeamID=team_id)

    return render(request, 'DevSign_Vote/session-select.html', {
        'sessions': sessions,
        'departments': Department.objects.all(),
        'teams': Team.objects.all()
    })


@login_required
@csrf_exempt
def join_session(request, session_id):
    session = get_object_or_404(Session, pk=session_id)
    cards = session.health_cards.all()

    if request.method == "POST":
        for card in cards:
            vote_value = request.POST.get(f"vote_{card.CardID}")
            trend = request.POST.get(f"trend_{card.CardID}")
            comment = request.POST.get(f"comment_{card.CardID}")
            if vote_value and trend:
                Vote.objects.create(
                    TeamID=request.user.TeamID,
                    UserID=request.user,
                    CardID=card,
                    SessionID=session,
                    VoteValue=vote_value,
                    Progress=trend,
                    Comment=comment
                )
        messages.success(request, "Votes submitted successfully.")
        return redirect("confirmation", session_id=session.SessionID)

    return render(request, 'DevSign_Vote/voting.html', {
        "session": session,
        "cards": cards
    })


@login_required
@csrf_exempt
def confirmation_view(request, session_id):
    session = get_object_or_404(Session, pk=session_id)
    return render(request, "DevSign_Vote/confirmation.html", {"session": session})


@login_required
def portal_view(request):
    user = request.user
    if user.role == "engineer":
        messages.error(request, "You are not authorized to access the portal.")
        return redirect("home")

    context = {'user': user}
    health_cards = HealthCard.objects.all()
    context['health_cards'] = health_cards

    def calculate_trends(votes):
        trends = defaultdict(str)
        for vote in votes:
            if vote.CardID and vote.Progress:
                trends[vote.CardID.Description] = vote.Progress
        return trends

    # TEAM LEADER VIEW
    if user.role == "team_leader":
        sessions = Session.objects.filter(UserID=user).order_by('-StartTime')
        context["team_sessions"] = sessions
        latest = sessions.first()
        if latest:
            votes = Vote.objects.filter(SessionID=latest)
            context["department_summary"] = [{
                "TeamName": user.TeamID.Name if user.TeamID else "Unknown",
                **votes.aggregate(
                    RedVotes=Count("VoteID", filter=Q(VoteValue=1)) or 0,
                    YellowVotes=Count("VoteID", filter=Q(VoteValue=2)) or 0,
                    GreenVotes=Count("VoteID", filter=Q(VoteValue=3)) or 0
                )
            }]
            context["section_trends"] = calculate_trends(votes)
        else:
            context["department_summary"] = [{
                "TeamName": user.TeamID.Name if user.TeamID else "Unknown",
                "RedVotes": 0, "YellowVotes": 0, "GreenVotes": 0
            }]
            context["section_trends"] = {}

    # DEPARTMENT LEADER VIEW
    elif user.role == "department_leader":
        department = user.TeamID.DepartmentID if user.TeamID and user.TeamID.DepartmentID else None
        teams = Team.objects.filter(DepartmentID=department) if department else Team.objects.none()
        context["teams"] = teams
        context["departments"] = Department.objects.all()

        selected_team = request.GET.get("team")
        selected_session = request.GET.get("session")

        sessions = Session.objects.filter(TeamID__in=teams)
        if selected_team:
            sessions = sessions.filter(TeamID=selected_team)
        if selected_session:
            sessions = sessions.filter(SessionID=selected_session)
        context["sessions"] = sessions

        summary = []
        vote_data = {}
        for team in teams:
            team_sessions = Session.objects.filter(TeamID=team).order_by('-StartTime')
            team_votes = Vote.objects.filter(TeamID=team)

            # Summary for the UI
            summary.append({
                "TeamName": team.Name,
                "Sessions": team_sessions,
                "RedVotes": team_votes.filter(VoteValue=1).count(),
                "YellowVotes": team_votes.filter(VoteValue=2).count(),
                "GreenVotes": team_votes.filter(VoteValue=3).count()
            })

            # Session vote breakdown for charts
            vote_data[team.Name] = {}
            for session in team_sessions:
                session_votes = Vote.objects.filter(SessionID=session)
                vote_data[team.Name][session.session_name] = {
                    "RedVotes": session_votes.filter(VoteValue=1).count(),
                    "YellowVotes": session_votes.filter(VoteValue=2).count(),
                    "GreenVotes": session_votes.filter(VoteValue=3).count(),
                    "StartTime": str(session.StartTime),
                    "EndTime": str(session.EndTime),
                    "Status": session.Status
                }

        context["department_summary"] = summary
        context["section_trends"] = calculate_trends(Vote.objects.filter(TeamID__in=teams))
        context["vote_data"] = json.dumps(vote_data)

    # SENIOR ENGINEER VIEW
    elif user.role == "senior_engineer":
        departments = Department.objects.all()
        context["departments"] = departments

        selected_dept = request.GET.get("department")
        selected_team = request.GET.get("team")
        selected_session = request.GET.get("session")

        sessions = Session.objects.all()
        if selected_dept:
            sessions = sessions.filter(DepartmentID=selected_dept)
        if selected_team:
            sessions = sessions.filter(TeamID=selected_team)
        if selected_session:
            sessions = sessions.filter(SessionID=selected_session)
        context["sessions"] = sessions

        company_summary = []
        vote_data = {}

        for dept in departments:
            teams = Team.objects.filter(DepartmentID=dept)
            team_data = []

            for team in teams:
                team_votes = Vote.objects.filter(TeamID=team)
                team_sessions = Session.objects.filter(TeamID=team).order_by('-StartTime')

                # Summary for team within department
                team_data.append({
                    "TeamName": team.Name,
                    "Sessions": team_sessions,
                    "RedVotes": team_votes.filter(VoteValue=1).count(),
                    "YellowVotes": team_votes.filter(VoteValue=2).count(),
                    "GreenVotes": team_votes.filter(VoteValue=3).count()
                })

                # Session vote data for chart
                vote_data[team.Name] = {}
                for session in team_sessions:
                    session_votes = Vote.objects.filter(SessionID=session)
                    vote_data[team.Name][session.session_name] = {
                        "RedVotes": session_votes.filter(VoteValue=1).count(),
                        "YellowVotes": session_votes.filter(VoteValue=2).count(),
                        "GreenVotes": session_votes.filter(VoteValue=3).count(),
                        "StartTime": str(session.StartTime),
                        "EndTime": str(session.EndTime),
                        "Status": session.Status
                    }

            company_summary.append({
                "DepartmentName": dept.DepartmentName,
                "Teams": team_data
            })

        context["company_summary"] = company_summary
        context["section_trends"] = calculate_trends(Vote.objects.all())
        context["vote_data"] = json.dumps(vote_data)

    return render(request, "DevSign_Vote/portal.html", context)
