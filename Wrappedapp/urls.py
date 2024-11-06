"""URL routing for Wrappedapp."""

from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # Home page
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('dashboard/', views.dashboard, name='dashboard'),  # Dashboard route
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),    # Custom logout page
    path('home/', views.home, name='home'),  # Home page route
    path("your-django-endpoint/", views.my_data_view, name="my_data_view"),
    path('spotify-authorize/', views.spotify_authorize, name='spotify_authorize'),
    path('dashboard/', views. dashboard, name='dashboard'),
    path('spot_login/', views.spot_login, name='spot_login'),
    path('callback/', views.callback, name='callback'),
    path('top_songs/', views.top_songs, name='top_songs'),
    path('unlink/', views.unlink, name='unlink'),

]
