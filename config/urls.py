from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from apps.core.views import DashboardView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', DashboardView.as_view(), name='dashboard'),
    path('accounts/', include('apps.accounts.urls')),
    path('organization/', include('apps.organization.urls')),
    path('employees/', include('apps.employees.urls')),
    path('onboarding/', include('apps.onboarding.urls')),
    path('offboarding/', include('apps.offboarding.urls')),
    path('recruitment/', include('apps.recruitment.urls')),
    path('attendance/', include('apps.attendance.urls')),
    path('payroll/', include('apps.payroll.urls')),
    path('performance/', include('apps.performance.urls')),
    path('training/', include('apps.training.urls')),
    path('ess/', include('apps.ess.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
