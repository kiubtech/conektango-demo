from django.apps import AppConfig


class ConektangoConfig(AppConfig):
    name = 'conektango'

    def ready(self):
        import conektango.signals
