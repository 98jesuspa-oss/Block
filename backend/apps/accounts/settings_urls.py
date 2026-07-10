from django.urls import path
from . import settings_views

app_name = 'config'
urlpatterns = [
    path('', settings_views.settings_view, name='index'),
    path('empresa/', settings_views.company_save, name='empresa'),
    path('users/form/', settings_views.user_form, name='user_form'),
    path('users/<int:pk>/form/', settings_views.user_form, name='user_form_edit'),
    path('users/<int:pk>/edit/', settings_views.user_edit, name='user_edit'),
    path('company/', settings_views.company_save, name='company_save'),
]