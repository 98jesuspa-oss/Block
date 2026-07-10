from django.urls import path
from . import views

app_name = 'customers'

urlpatterns = [
    path('', views.customers_list, name='index'),
    path('table/', views.customer_table, name='table'),
    path('search/', views.customer_search, name='search'),
    path('form/', views.customer_form, name='form'),
    path('<int:pk>/form/', views.customer_form, name='form_edit'),
    path('create/', views.customer_create, name='create'),
    path('<int:pk>/update/', views.customer_update, name='update'),
]