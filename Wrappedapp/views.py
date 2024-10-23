from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import SignUpForm
from django.contrib.auth.decorators import login_required
# Create your views here.
# Wrappedapp/views.py

def home(request):
    return render(request, 'home.html')  # Render the home page template

def register(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Log the user in after registration
            return redirect('dashboard')  # Redirect to dashboard after registering
    else:
        form = SignUpForm()

    return render(request, 'register.html', {'form': form})

@login_required
def dashboard(request):
    return render(request, 'dashboard.html')
