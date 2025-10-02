import os 
from django.conf import settings 
from django.conf.urls.static import static 
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Django Admin Site
    path('admin/', admin.site.urls),
    
    # API Endpoints
    path('api/', include(('accounts.urls', 'accounts'), namespace='accounts')),
    path('api/menu/', include('menu.urls')),
    path('api/orders/', include('orders.urls')),
    path('api/tables/', include('tables.urls')),
    path('api/inventory/', include('inventory.urls')),
    path('api/dashboard/', include('dashboard_stats.urls')),
    path('api/guests/', include('guests.urls')),
    path('api/service-requests/', include('service_requests.urls')),
    path('api/payments/', include('payments.urls')),
    path('api/receipts/', include('receipts.urls')),
    path('api/reports/', include('reports.urls')),
]

# --- CRITICAL FIX FOR SERVING MEDIA FILES DURING DEVELOPMENT ---
if settings.DEBUG:
    # This pattern serves media files (images, files) uploaded by users.
    # It MUST be active in development for images to load.
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
    # Also include static files for robustness
    urlpatterns += static(settings.STATIC_URL, document_root=os.path.join(settings.BASE_DIR, 'staticfiles'))
