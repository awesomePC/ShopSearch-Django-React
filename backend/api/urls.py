from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns=[
    path('', views.all_items),
    # path('download-image/', views.all_items),
    path('search-history/', views.search_history),
    path('offline-items/', views.offline_items),
    path('online-items/', views.online_items),
   
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
