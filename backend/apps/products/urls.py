from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('', views.products_list, name='index'),
    path('table/', views.product_table, name='table'),
    path('form/', views.product_form, name='form'),
    path('<int:pk>/form/', views.product_form, name='form_edit'),
    path('create/', views.product_form, name='create'),
    path('<int:pk>/update/', views.product_form, name='update'),
    path('<int:pk>/delete/', views.product_delete, name='delete'),
    path('<int:pk>/movements/', views.product_movements_json, name='movements'),
    path('<int:pk>/movement/', views.product_movement, name='movement'),
    path('pos-search/', views.product_pos_search, name='pos_search'),
]