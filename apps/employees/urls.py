from django.urls import path
from . import views

app_name = 'employees'

urlpatterns = [
    path('', views.EmployeeDirectoryView.as_view(), name='directory'),
    path('create/', views.EmployeeCreateView.as_view(), name='create'),
    path('<int:pk>/', views.EmployeeDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.EmployeeUpdateView.as_view(), name='edit'),
    path('<int:pk>/delete/', views.EmployeeDeleteView.as_view(), name='delete'),
    # Documents
    path('<int:pk>/documents/', views.EmployeeDocumentsView.as_view(), name='documents'),
    path('<int:pk>/documents/upload/', views.DocumentUploadView.as_view(), name='document_upload'),
    path('documents/<int:pk>/delete/', views.DocumentDeleteView.as_view(), name='document_delete'),
    # Lifecycle
    path('<int:pk>/lifecycle/', views.EmployeeLifecycleView.as_view(), name='lifecycle'),
    path('<int:pk>/lifecycle/add/', views.LifecycleEventCreateView.as_view(), name='lifecycle_add'),
]
