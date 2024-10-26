from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import SignUpForm
from django.contrib.auth.decorators import login_required
from decouple import config
from django.http import JsonResponse
from django.conf import settings
import urllib.parse

import requests
from django.shortcuts import redirect
from django.conf import settings

client_id = settings.SPOTIFY_CLIENT_ID
client_secret = settings.SPOTIFY_CLIENT_SECRET
redirect_uri = settings.SPOTIFY_REDIRECT_URI


# Create your views here.
# Wrappedapp/views.py

def home(request):
    access_token = request.session.get("access_token", "")
    return render(request, "home.html", {"access_token": access_token})


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

def spotify_connect(request):
    spotify_auth_url = "https://accounts.spotify.com/authorize"
    client_id =  config('SPOTIFY_CLIENT_ID')
    redirect_uri = config('SPOTIFY_REDIRECT_URI')
    scope = "user-top-read"  # Adjust based on your needs

    auth_url = f"{spotify_auth_url}?response_type=code&client_id={client_id}&redirect_uri={redirect_uri}&scope={scope}"
    return redirect(auth_url)

def my_data_view(request):
    data = {"message": "Hello from Django!"}
    return JsonResponse(data)

def spotify_authorize(request):
    spotify_auth_url = "https://accounts.spotify.com/authorize"
    params = {
        "client_id": settings.SPOTIFY_CLIENT_ID,
        "response_type": "code",
        "redirect_uri": settings.SPOTIFY_REDIRECT_URI,
        "scope": "user-top-read",  # Add other scopes as needed
    }
    auth_url = f"{spotify_auth_url}?{urllib.parse.urlencode(params)}"
    return redirect(auth_url)

def spotify_callback(request):
    code = request.GET.get("code")
    token_url = "https://accounts.spotify.com/api/token"

    response = requests.post(token_url, data={
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": settings.SPOTIFY_REDIRECT_URI,
        "client_id": settings.SPOTIFY_CLIENT_ID,
        "client_secret": settings.SPOTIFY_CLIENT_SECRET,
    })

    if response.status_code == 200:
        tokens = response.json()
        access_token = tokens["access_token"]
        refresh_token = tokens["refresh_token"]

        # Save tokens in the session (or database) for later use
        request.session["access_token"] = access_token
        request.session["refresh_token"] = refresh_token

        # Redirect to another view, or render a template
        return redirect("home")  # Change 'home' to your target URL
    else:
        return redirect("error")  # Handle errors gracefully