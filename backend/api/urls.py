from django.urls import path
from . import views

urlpatterns=[
    path('', views.all_items),
    path('download-image/', views.download_images),
    # path('<int:pk>/', views.djqueue_detail),
]