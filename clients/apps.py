from django.apps import AppConfig


class ClientsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'clients'

    # Это нужно, чтобы при старте приложения, у нас подключались сигналы, без всяких проблем с циклическими импортами
    def ready(self):
        import clients.signals