from django.apps import AppConfig

class loansConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'loans'

    def ready(self):
        import loans.signal  # Ensure this is executed when your app is ready
