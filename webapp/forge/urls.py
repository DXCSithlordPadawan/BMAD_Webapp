"""
URL patterns for BMAD Forge application.
"""

from django.urls import path
from . import views

app_name = 'forge'

urlpatterns = [
    # Health check endpoint (for monitoring)
    path('health/', views.health_check, name='health_check'),

    # Dashboard
    path('', views.DashboardView.as_view(), name='dashboard'),

    # Template URLs
    path('templates/', views.TemplateListView.as_view(), name='template_list'),
    path('templates/<int:pk>/', views.TemplateDetailView.as_view(), name='template_detail'),

    # Prompt URLs
    path('generate/<int:template_id>/', views.PromptFormView.as_view(), name='prompt_form'),
    path('prompts/<int:pk>/', views.PromptResultView.as_view(), name='prompt_result'),
    path('prompts/history/', views.PromptHistoryView.as_view(), name='prompt_history'),
    path('prompts/<int:pk>/download/', views.download_prompt, name='download_prompt'),

    # Document Generation URLs
    path('generate-document/', views.GenerateDocumentSelectView.as_view(), name='generate_document_select'),
    path('generate-document/<int:template_id>/', views.GenerateDocumentWizardView.as_view(), name='generate_document_wizard'),
    path('generate-document/<int:template_id>/validate/', views.validate_section_realtime, name='validate_section_realtime'),
    path('generate-document/<int:template_id>/guidance/<str:section_name>/', views.get_section_guidance, name='get_section_guidance'),
    path('generate-document/<int:template_id>/validate-variable/', views.validate_variable, name='validate_variable'),
    path('generate-document/<int:template_id>/completion-status/', views.get_completion_status, name='get_completion_status'),
    path('generate-document/<int:template_id>/steps/', views.get_enhanced_wizard_steps, name='get_enhanced_wizard_steps'),

    # GitHub Sync URLs
    path('sync/', views.GitHubSyncView.as_view(), name='github_sync'),
    path('sync/manual/', views.manual_sync, name='manual_sync'),
]
