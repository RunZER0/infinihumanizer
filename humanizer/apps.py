from django.apps import AppConfig


class HumanizerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'humanizer'
    
    def ready(self):
        """Initialize NLTK data when Django starts"""
        pass  # NLTK punkt will be downloaded on first use if needed
