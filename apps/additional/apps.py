from django.apps import AppConfig


class AdditionalConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.additional'
    verbose_name = 'Additional Modules'
