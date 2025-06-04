from django.apps import AppConfig

class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.users'    # → Python import 경로
    label = 'apps_users'        # → Django가 인식할 app_label
