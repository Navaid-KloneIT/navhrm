from django.urls import path
from . import views

app_name = 'recruitment'

urlpatterns = [
    # Job Requisitions
    path('jobs/', views.JobListView.as_view(), name='job_list'),
    path('jobs/create/', views.JobCreateView.as_view(), name='job_create'),
    path('jobs/<int:pk>/', views.JobDetailView.as_view(), name='job_detail'),
    path('jobs/<int:pk>/edit/', views.JobUpdateView.as_view(), name='job_edit'),
    path('jobs/<int:pk>/delete/', views.JobDeleteView.as_view(), name='job_delete'),
    # Job Templates
    path('templates/', views.JobTemplateListView.as_view(), name='template_list'),
    path('templates/create/', views.JobTemplateCreateView.as_view(), name='template_create'),
    path('templates/<int:pk>/edit/', views.JobTemplateUpdateView.as_view(), name='template_edit'),
    path('templates/<int:pk>/delete/', views.JobTemplateDeleteView.as_view(), name='template_delete'),
    # Candidates
    path('candidates/', views.CandidateListView.as_view(), name='candidate_list'),
    path('candidates/create/', views.CandidateCreateView.as_view(), name='candidate_create'),
    path('candidates/<int:pk>/', views.CandidateDetailView.as_view(), name='candidate_detail'),
    path('candidates/<int:pk>/edit/', views.CandidateUpdateView.as_view(), name='candidate_edit'),
    path('candidates/<int:pk>/delete/', views.CandidateDeleteView.as_view(), name='candidate_delete'),
    # Applications
    path('applications/', views.ApplicationListView.as_view(), name='application_list'),
    path('applications/<int:pk>/', views.ApplicationDetailView.as_view(), name='application_detail'),
    path('applications/<int:pk>/edit/', views.ApplicationUpdateView.as_view(), name='application_edit'),
    path('applications/<int:pk>/delete/', views.ApplicationDeleteView.as_view(), name='application_delete'),
    # Interviews
    path('interviews/', views.InterviewListView.as_view(), name='interview_list'),
    path('interviews/create/', views.InterviewCreateView.as_view(), name='interview_create'),
    path('interviews/<int:pk>/', views.InterviewDetailView.as_view(), name='interview_detail'),
    path('interviews/<int:pk>/edit/', views.InterviewUpdateView.as_view(), name='interview_edit'),
    path('interviews/<int:pk>/delete/', views.InterviewDeleteView.as_view(), name='interview_delete'),
    # Feedback
    path('interviews/<int:pk>/feedback/', views.FeedbackCreateView.as_view(), name='feedback_create'),
    path('interviews/<int:pk>/feedback/<int:fpk>/edit/', views.FeedbackUpdateView.as_view(), name='feedback_edit'),
    # Offers
    path('offers/', views.OfferListView.as_view(), name='offer_list'),
    path('offers/create/', views.OfferCreateView.as_view(), name='offer_create'),
    path('offers/<int:pk>/', views.OfferDetailView.as_view(), name='offer_detail'),
    path('offers/<int:pk>/edit/', views.OfferUpdateView.as_view(), name='offer_edit'),
    path('offers/<int:pk>/delete/', views.OfferDeleteView.as_view(), name='offer_delete'),
    # Public Career Page
    path('careers/', views.CareerPageView.as_view(), name='career_page'),
    path('careers/success/', views.CareerSuccessView.as_view(), name='career_success'),
    path('careers/<int:pk>/', views.CareerDetailView.as_view(), name='career_detail'),
    path('careers/<int:pk>/apply/', views.CareerApplyView.as_view(), name='career_apply'),
]
