# Generated by Django 4.2 on 2024-12-01 01:45

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("Wrappedapp", "0002_spotifywrapped_personality_word_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="spotifywrapped",
            name="is_public",
            field=models.BooleanField(default=False),
        ),
    ]
