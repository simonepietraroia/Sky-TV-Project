from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate  
from django.contrib.auth.forms import AuthenticationForm
from .forms import UserRegisterForm, ProfileUpdateForm, EmailAuthenticationForm
import base64
from django.core.files.base import ContentFile
from django.views.decorators.csrf import csrf_exempt
# from .models import Session, Vote, Team, Department, AggregateVotesTable, TrendAnalysis


def homepage(request):
    return render(request, 'DevSign_Vote/home.html')

def user_login(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home') 
        else:
            messages.error(request, "Invalid username or password")
    return render(request, 'DevSign_Vote/login.html')

@login_required
def profile(request):
    return render(request, "DevSign_Vote/profile.html")

@login_required
def edit_profile(request):
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