from django.apps import AppConfig


class WrappedappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Wrappedapp'
