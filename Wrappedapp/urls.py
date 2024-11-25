"""URL routing for Wrappedapp."""

from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # Home page
    path('home/', views.home, name='home'),  # Home page route
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('dashboard/', views.dashboard, name='dashboard'),  # Dashboard route
    path('logout/', views.custom_logout_view, name='logout'),    # Custom logout page
    path('spotify-authorize/', views.spotify_authorize, name='spotify_authorize'),
    path('callback/', views.spotify_callback, name='spotify_callback'),
    path('unlink/', views.unlink, name='unlink'),
    path('contact/', views.contact_developers, name='contact_developers'),
    path('create_wrapped/', views.create_wrapped, name='create_wrapped'),
    path('wrapped_carousel/<int:wrapped_id>/', views.wrapped_carousel, name='wrapped_carousel'),



]
