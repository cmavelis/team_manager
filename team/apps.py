from django.apps import AppConfig


class PeopleConfig(AppConfig):
    name = 'team'

    def ready(self):
        import team.signals
