from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import ProfileUpdateForm

def homepage(request):
    return render(request, 'DevSign_Vote/home.html')

#@login_required
def profile(request):
    return render(request, "DevSign_Vote/profile.html")

#@login_required
def edit_profile(request):
    if request.method == "POST":
        form = ProfileUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated!")
            return redirect("profile")
    else:
        form = ProfileUpdateForm(instance=request.user)

    return render(request, "DevSign_Vote/edit_profile.html", {"form": form})