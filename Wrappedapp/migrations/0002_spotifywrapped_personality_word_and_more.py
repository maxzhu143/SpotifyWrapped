# Generated by Django 4.2 on 2024-11-29 01:01

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("Wrappedapp", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="spotifywrapped",
            name="personality_word",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name="spotifywrapped",
            name="top_songs",
            field=models.JSONField(default=list),
        ),
    ]
