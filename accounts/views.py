from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from accounts.forms import RegisterForm, UserProfileForm
from accounts.models import UserProfile

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            # UserProfile is created automatically by the post_save signal on the User model
            login(request, user)
            return redirect('accounts:profile')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})

@login_required
def profile_view(request):
    # Fetch or create to safely handle signal failures
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            profile_instance = form.save(commit=False)
            profile_instance.profile_complete = True
            profile_instance.save()
            return redirect('/')  # Redirects to dashboard root
    else:
        form = UserProfileForm(instance=profile)
        
    return render(request, 'accounts/profile.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('/')  # Redirects to dashboard root
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('accounts:login')
