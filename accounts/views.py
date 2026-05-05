from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from accounts.forms import RegisterForm, UserProfileForm, AccountSettingsForm, ProfileImageForm
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

@login_required
def settings_view(request):
    if request.method == 'POST':
        form = AccountSettingsForm(request.POST, instance=request.user)
        image_form = ProfileImageForm(request.POST, request.FILES, instance=request.user.profile)
        
        # Check if user is attempting to change password
        old_password = request.POST.get('old_password')
        if old_password:
            password_form = PasswordChangeForm(user=request.user, data=request.POST)
            if form.is_valid() and image_form.is_valid() and password_form.is_valid():
                form.save()
                image_form.save()
                user = password_form.save()
                update_session_auth_hash(request, user)  # Keeps user logged in
                messages.success(request, 'Your account settings and password were successfully updated.')
                return redirect('accounts:settings')
        else:
            password_form = PasswordChangeForm(user=request.user)
            if form.is_valid() and image_form.is_valid():
                form.save()
                image_form.save()
                messages.success(request, 'Your account settings were successfully updated.')
                return redirect('accounts:settings')
    else:
        form = AccountSettingsForm(instance=request.user)
        image_form = ProfileImageForm(instance=request.user.profile)
        password_form = PasswordChangeForm(user=request.user)
        
    return render(request, 'accounts/settings.html', {
        'form': form,
        'image_form': image_form,
        'password_form': password_form
    })

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
