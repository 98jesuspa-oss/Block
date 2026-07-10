from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('apps.accounts.urls', namespace='accounts')),
    path('products/', include('apps.products.urls', namespace='products')),
    path('customers/', include('apps.customers.urls', namespace='customers')),
    path('reports/', include('apps.reports.urls', namespace='reports')),
    path('settings/', include('apps.accounts.settings_urls', namespace='config')),
    path('sales/', include('apps.sales.urls', namespace='sales')),
    path('', include('apps.sales.dashboard_urls', namespace='dashboard')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
