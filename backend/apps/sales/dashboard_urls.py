from django.urls import path
from apps.sales import dashboard_views

app_name = 'dashboard'
urlpatterns = [
    path('', dashboard_views.dashboard, name='index'),
]