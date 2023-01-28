from django.urls import path
from . import views

urlpatterns=[
    path('', views.all_items),
    path('download-image/', views.all_items),
    path('search-history/', views.search_history),
    path('offlie-items/', views.offline_items),
   
]