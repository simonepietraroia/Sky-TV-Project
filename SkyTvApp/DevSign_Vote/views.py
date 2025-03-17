from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import ProfileUpdateForm
# from .models import Session, Vote, Team, Department, AggregateVotesTable, TrendAnalysis


def homepage(request):
    """ Renders the homepage """
    return render(request, 'DevSign_Vote/home.html')

def user_login(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')  # Redirect to home or dashboard
        else:
            messages.error(request, "Invalid username or password")
    return render(request, 'DevSign_Vote/login.html')

@login_required
def profile(request):
    """ Renders the user profile page """
    return render(request, "DevSign_Vote/profile.html")

@login_required
def edit_profile(request):
    """ Allows users to edit their profile """
    if request.method == "POST":
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated!")
            return redirect("profile")
    else:
        form = ProfileUpdateForm(instance=request.user)

    return render(request, "DevSign_Vote/edit_profile.html", {"form": form})


@login_required
def portal_view(request):
    """ 
    Renders the portal page dynamically based on user roles.
    """
    user = request.user
    context = {'user': user}

    if user.role == "team_leader":
        context['team_sessions'] = Session.objects.filter(UserID=user.UserID)

    elif user.role == "department_leader":
        teams = Team.objects.filter(DepartmentID=user.TeamID.DepartmentID)
        context['department_summary'] = AggregateVotesTable.objects.filter(TeamID__in=teams)
        context['department_trends'] = TrendAnalysis.objects.filter(TeamID__in=teams)

    elif user.role == "senior_engineer":
        context['company_summary'] = AggregateVotesTable.objects.all()
        context['company_trends'] = TrendAnalysis.objects.all()

    return render(request, 'DevSign_Vote/portal.html', context)


@login_required
def create_voting_session(request):
    """ 
    Allows Team Leaders to create a new voting session.
    """
    if request.method == "POST":
        if request.user.role != "team_leader":
            messages.error(request, "You do not have permission to create a voting session.")
            return redirect('portal')

        session_title = request.POST.get("title")
        new_session = Session.objects.create(
            UserID=request.user,
            Status="Open",
            CreatedBy=request.user,
        )
        messages.success(request, f"Voting session '{session_title}' created successfully!")
        return redirect('portal')

    return redirect('portal')