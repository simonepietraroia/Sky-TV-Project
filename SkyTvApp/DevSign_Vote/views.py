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
            return redirect('profile')
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
def portal_view(request):
    user = request.user
    if user.role == "engineer":
        messages.error(request, "You are not authorized to view this page.")
        return redirect('home')

    context = {'user': user}
    health_cards = HealthCard.objects.all()
    context['health_cards'] = health_cards

    def calculate_section_trends(votes_queryset):
        trends = defaultdict(str)
        for vote in votes_queryset:
            if vote.CardID and vote.Progress:
                trends[vote.CardID.Description] = vote.Progress
        return trends

    if user.role == "team_leader":
        sessions = Session.objects.filter(UserID=user).order_by('-StartTime')
        context['team_sessions'] = sessions
        latest_session = sessions.first()
        if latest_session:
            vote_counts = Vote.objects.filter(SessionID=latest_session).aggregate(
                RedVotes=Count('VoteID', filter=Q(VoteValue=1)) or 0,
                YellowVotes=Count('VoteID', filter=Q(VoteValue=2)) or 0,
                GreenVotes=Count('VoteID', filter=Q(VoteValue=3)) or 0,
            )
            vote_counts['RedVotes'] = vote_counts['RedVotes'] or 0
            vote_counts['YellowVotes'] = vote_counts['YellowVotes'] or 0
            vote_counts['GreenVotes'] = vote_counts['GreenVotes'] or 0
            vote_counts['TotalVotes'] = vote_counts['RedVotes'] + vote_counts['YellowVotes'] + vote_counts['GreenVotes']
            context['department_summary'] = [vote_counts]
            section_votes = Vote.objects.filter(SessionID=latest_session)
            context['section_trends'] = calculate_section_trends(section_votes)
        else:
            context['department_summary'] = [{"RedVotes": 0, "YellowVotes": 0, "GreenVotes": 0, "TotalVotes": 0}]
            context['section_trends'] = {}

    elif user.role == "department_leader":
        teams = Team.objects.filter(DepartmentID=user.TeamID.DepartmentID)
        context['teams'] = teams
        selected_team_id = request.GET.get('team')
        selected_session_id = request.GET.get('session')
        sessions = Session.objects.filter(TeamID__in=teams)
        if selected_team_id:
            sessions = sessions.filter(TeamID=selected_team_id)
        if selected_session_id:
            sessions = sessions.filter(SessionID=selected_session_id)
        vote_data = []
        for team in teams:
            votes = Vote.objects.filter(TeamID=team)
            if votes.exists():
                aggregated = votes.aggregate(
                    RedVotes=Count('VoteID', filter=Q(VoteValue=1)) or 0,
                    YellowVotes=Count('VoteID', filter=Q(VoteValue=2)) or 0,
                    GreenVotes=Count('VoteID', filter=Q(VoteValue=3)) or 0
                )
                aggregated['RedVotes'] = aggregated['RedVotes'] or 0
                aggregated['YellowVotes'] = aggregated['YellowVotes'] or 0
                aggregated['GreenVotes'] = aggregated['GreenVotes'] or 0
                aggregated['TeamID'] = team
                aggregated['TotalVotes'] = aggregated['RedVotes'] + aggregated['YellowVotes'] + aggregated['GreenVotes']
                vote_data.append(aggregated)
        context['department_summary'] = vote_data
        context['sessions'] = sessions
        context['section_trends'] = calculate_section_trends(Vote.objects.filter(TeamID__in=teams))

    elif user.role == "senior_engineer":
        departments = Department.objects.all()
        selected_dept_id = request.GET.get('department')
        selected_team_id = request.GET.get('team')
        selected_session_id = request.GET.get('session')

        sessions = Session.objects.all()
        if selected_dept_id:
            sessions = sessions.filter(DepartmentID=selected_dept_id)
        if selected_team_id:
            sessions = sessions.filter(TeamID=selected_team_id)
        if selected_session_id:
            sessions = sessions.filter(SessionID=selected_session_id)

        vote_data = []
        for dept in departments:
            votes = Vote.objects.filter(TeamID__DepartmentID=dept)
            if votes.exists():
                aggregated = votes.aggregate(
                    RedVotes=Count('VoteID', filter=Q(VoteValue=1)) or 0,
                    YellowVotes=Count('VoteID', filter=Q(VoteValue=2)) or 0,
                    GreenVotes=Count('VoteID', filter=Q(VoteValue=3)) or 0
                )
                aggregated['RedVotes'] = aggregated['RedVotes'] or 0
                aggregated['YellowVotes'] = aggregated['YellowVotes'] or 0
                aggregated['GreenVotes'] = aggregated['GreenVotes'] or 0
                team = Team.objects.filter(DepartmentID=dept).first()
                aggregated['TeamID'] = team
                aggregated['TeamID'].DepartmentID = dept
                aggregated['TotalVotes'] = aggregated['RedVotes'] + aggregated['YellowVotes'] + aggregated['GreenVotes']
                vote_data.append(aggregated)

        context['departments'] = departments
        context['company_summary'] = vote_data
        context['sessions'] = sessions
        context['section_trends'] = calculate_section_trends(Vote.objects.all())

    return render(request, 'DevSign_Vote/portal.html', context)
