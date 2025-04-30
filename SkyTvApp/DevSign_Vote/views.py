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


def homepage(request):
    return render(request, 'DevSign_Vote/home.html')


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
def portal_view(request, session_id=None):
    user = request.user
    context = {'user': user}

    def calculate_section_trends(votes_queryset):
        trends = defaultdict(str)
        for vote in votes_queryset:
            if vote.CardID and vote.Progress:
                trends[vote.CardID.Description] = vote.Progress
        return trends

    if user.role == "team_leader":
        sessions = Session.objects.filter(UserID=user)
        context['team_sessions'] = sessions

        latest_session = sessions.order_by('-StartTime').first()
        if latest_session:
            vote_counts = Vote.objects.filter(SessionID=latest_session).aggregate(
                RedVotes=Count('VoteID', filter=Q(VoteValue=1)),
                YellowVotes=Count('VoteID', filter=Q(VoteValue=2)),
                GreenVotes=Count('VoteID', filter=Q(VoteValue=3)),
            )
            vote_counts['TotalVotes'] = sum(vote_counts.values())
            context['department_summary'] = [vote_counts]

            section_votes = Vote.objects.filter(SessionID=latest_session)
            context['section_trends'] = calculate_section_trends(section_votes)
        else:
            context['department_summary'] = []
            context['section_trends'] = {}

    elif user.role == "department_leader":
        teams = Team.objects.filter(DepartmentID=user.TeamID.DepartmentID)
        vote_data = []

        for team in teams:
            votes = Vote.objects.filter(TeamID=team)
            if votes.exists():
                aggregated = votes.aggregate(
                    RedVotes=Count('VoteID', filter=Q(VoteValue=1)),
                    YellowVotes=Count('VoteID', filter=Q(VoteValue=2)),
                    GreenVotes=Count('VoteID', filter=Q(VoteValue=3))
                )
                aggregated['TeamID'] = team
                aggregated['TotalVotes'] = sum(aggregated.values())
                vote_data.append(aggregated)

        context['department_summary'] = vote_data
        section_votes = Vote.objects.filter(TeamID__in=teams)
        context['section_trends'] = calculate_section_trends(section_votes)

    elif user.role == "senior_engineer":
        departments = Department.objects.all()
        vote_data = []

        for dept in departments:
            votes = Vote.objects.filter(TeamID__DepartmentID=dept)
            if votes.exists():
                aggregated = votes.aggregate(
                    RedVotes=Count('VoteID', filter=Q(VoteValue=1)),
                    YellowVotes=Count('VoteID', filter=Q(VoteValue=2)),
                    GreenVotes=Count('VoteID', filter=Q(VoteValue=3))
                )
                team = Team.objects.filter(DepartmentID=dept).first()
                aggregated['TeamID'] = team
                aggregated['TeamID'].DepartmentID = dept
                aggregated['TotalVotes'] = sum(aggregated.values())
                vote_data.append(aggregated)

        context['company_summary'] = vote_data
        section_votes = Vote.objects.all()
        context['section_trends'] = calculate_section_trends(section_votes)

    return render(request, 'DevSign_Vote/portal.html', context)

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
@csrf_exempt
def vote_on_session(request, session_id):
    session = Session.objects.get(pk=session_id)

    if session.Status == "Closed" or session.EndTime < timezone.now():
        messages.error(request, "This session is closed.")
        return redirect("portal", session_id=session.SessionID)


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

        if request.user.role == "engineer":
            return redirect("confirmation")
        else:
            return redirect("portal", session_id=session.SessionID)

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
        return redirect("portal", session_id=session.SessionID)


    return render(request, 'DevSign_Vote/voting.html', {
        'session': session,
        'cards': cards,
    })

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

@login_required
@csrf_exempt
def confirmation_view(request, session_id): 
    session = get_object_or_404(Session, pk=session_id)
    return render(request, 'DevSign_Vote/confirmation.html', {'session':session})