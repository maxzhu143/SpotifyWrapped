# Generated by Django 5.1.2 on 2024-11-25 12:40

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("Wrappedapp", "0004_alter_spotifyaccount_expires_at"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="SpotifyWrapped",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "title",
                    models.CharField(default="My Spotify Wrapped", max_length=255),
                ),
                ("top_songs", models.JSONField(default=dict)),
                ("top_artists", models.JSONField(default=dict)),
                ("top_genres", models.JSONField(default=dict)),
                (
                    "personality",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                ("total_minutes_listened", models.IntegerField(default=0)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="wrapped_objects",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
