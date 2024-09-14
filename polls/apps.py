"""Import Django app config."""
from django.apps import AppConfig


class PollsConfig(AppConfig):
    """Class for app config."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'polls'
