from django.urls import path
from . import views

app_name = 'sales'
urlpatterns = [
    path('', views.pos_view, name='pos'),
    path('create/', views.create_sale, name='create'),
    path('<int:pk>/nota/', views.sale_nota_by_pk, name='nota'),
    path('<str:folio>/nota/', views.sale_nota, name='nota_folio'),
    path('nota/<str:folio>/', views.sale_nota, name='nota_folio_alt'),
    path('nota/<int:pk>/', views.sale_nota_by_pk, name='nota_alt'),
]