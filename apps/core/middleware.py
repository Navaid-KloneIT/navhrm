from apps.core.models import set_current_tenant


class TenantMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and hasattr(request.user, 'tenant'):
            tenant = request.user.tenant
            request.tenant = tenant
            set_current_tenant(tenant)
        else:
            request.tenant = None
            set_current_tenant(None)

        response = self.get_response(request)
        set_current_tenant(None)
        return response
