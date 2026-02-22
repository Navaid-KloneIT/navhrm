from django.conf import settings


def tenant_context(request):
    return {
        'current_tenant': getattr(request, 'tenant', None),
        'app_name': getattr(settings, 'APP_NAME', 'NavHRM'),
    }
