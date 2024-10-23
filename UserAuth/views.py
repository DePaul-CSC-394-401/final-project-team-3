from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from .forms import UserEditForm
from django.contrib import messages

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Automatically log the user in after signup
            return redirect('dashboard')  # Redirect to dashboard after login
    else:
        form = UserCreationForm()
    return render(request, 'UserAuth/signup.html', {'form': form})


@login_required
def edit_user(request):
    user = request.user  # Get the current user
    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=user)
        if form.is_valid():
            # Only update if the new password is provided
            new_password = form.cleaned_data.get('new_password')
            if new_password:
                user.set_password(new_password)  # Set the new password

            # Update the username
            user.username = form.cleaned_data['username']  
            user.save()  # Save the user instance
            
            messages.success(request, 'Your account has been updated successfully!')
            return redirect('login')  # Redirect to login after editing
    else:
        form = UserEditForm(instance=user)

    return render(request, 'UserAuth/edit_user.html', {'form': form})