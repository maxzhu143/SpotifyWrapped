
"""URL routing for Wrappedapp."""

from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # Home page
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
    path('wrapped/delete/<int:wrapped_id>/', views.delete_wrapped, name='delete_wrapped'),
    path('save_wrapped/<int:wrapped_id>/', views.save_wrapped, name='save_wrapped'),
    path('discard_wrapped/<int:wrapped_id>/', views.discard_wrapped, name='discard_wrapped'),
    path('public-wraps/', views.public_wraps, name='public_wraps'),
    path('toggle-visibility/<int:wrapped_id>/', views.toggle_visibility, name='toggle_visibility'),

    path('translate', views.translate_text, name='translate_text'),
    path('translate-batch', views.translate_batch, name='translate_batch'),
    path('public-wraps/', views.public_wraps, name='public_wraps'),
    path('toggle-visibility/<int:wrapped_id>/', views.toggle_visibility, name='toggle_visibility'),

]