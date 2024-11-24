"""URL routing for Wrappedapp."""

from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    #path('', views.home, name='home'),  # Home page
    path('', views.welcome, name='welcome'),  # Home page
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('dashboard/', views.dashboard, name='dashboard'),  # Dashboard route
    path('logout/', views.custom_logout_view, name='logout'),    # Custom logout page
    path('home/', views.home, name='home'),  # Home page route
    path('spotify-authorize/', views.spotify_authorize, name='spotify_authorize'),
    path('spotify-callback/', views.spotify_callback, name='spotify_callback'),
    path('contact/', views.contact_developers, name='contact_developers'),
    path('dashboard/', views. dashboard, name='dashboard'),
    path('spot_login/', views.spot_login, name='spot_login'),
    path('callback/', views.callback, name='callback'),
    path('top_songs/', views.top_songs, name='top_songs'),
    path('unlink/', views.unlink, name='unlink'),
    path('stats/', views.stats_view, name='stats'),
    path('wrapped_carousel/', views.wrapped_carousel, name='wrapped_carousel'),
    path('track_click/', views.track_click, name='track_click'),

]
