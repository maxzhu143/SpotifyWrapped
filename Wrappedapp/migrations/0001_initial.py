# Generated by Django 4.2.15 on 2024-12-01 07:43

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='SpotifyAccount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('access_token', models.CharField(help_text='The access token for Spotify API requests.', max_length=500)),
                ('refresh_token', models.CharField(help_text='The refresh token for renewing the access token.', max_length=500)),
                ('expires_at', models.DateTimeField(blank=True, null=True)),
                ('display_name', models.CharField(blank=True, help_text='Spotify display name of the linked account.', max_length=500, null=True)),
                ('spotify_id', models.CharField(blank=True, help_text='The unique Spotify ID for the account.', max_length=500, null=True)),
                ('profile_url', models.URLField(blank=True, help_text="URL to the user's Spotify profile.", null=True)),
                ('profile_image', models.URLField(blank=True, help_text="URL to the user's Spotify profile image.", null=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='spotify_account', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='WrappedSummary',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.IntegerField(help_text='The year this summary covers.')),
                ('top_tracks', models.JSONField(help_text="JSON representation of the user's top tracks.")),
                ('top_artists', models.JSONField(help_text="JSON representation of the user's top artists.")),
                ('top_genres', models.JSONField(help_text="JSON representation of the user's top genres.")),
                ('listening_minutes', models.IntegerField(help_text='Total minutes listened during the year.')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('spotify_account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='wrapped_summaries', to='Wrappedapp.spotifyaccount')),
            ],
        ),
        migrations.CreateModel(
            name='SpotifyWrapped',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(default='My Spotify Wrapped', max_length=500)),
                ('top_songs', models.JSONField(default=list)),
                ('top_artists', models.JSONField(default=dict)),
                ('top_genres', models.JSONField(default=dict)),
                ('personality', models.CharField(blank=True, max_length=500, null=True)),
                ('total_minutes_listened', models.IntegerField(default=0)),
                ('sound_town', models.CharField(blank=True, max_length=500, null=True)),
                ('artist_thank_you', models.CharField(blank=True, max_length=500, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('top_podcasts', models.JSONField(default=dict)),
                ('personality_word', models.CharField(blank=True, max_length=500, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='wrapped_objects', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ListeningHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('track_name', models.CharField(max_length=500)),
                ('artist_name', models.CharField(max_length=500)),
                ('album_name', models.CharField(blank=True, max_length=500, null=True)),
                ('played_at', models.DateTimeField()),
                ('duration_ms', models.IntegerField(help_text='Duration of the track in milliseconds.')),
                ('spotify_account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='listening_history', to='Wrappedapp.spotifyaccount')),
            ],
        ),
    ]
