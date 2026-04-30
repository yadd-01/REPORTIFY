from django.urls import path
from . import views

urlpatterns = [
    path('', views.beranda, name='beranda'),
    path('<int:artikel_id>/', views.detail_berita, name='detail_berita'),
    
    # --- Tambahkan rute API ini ---
    path('api/berita/', views.api_berita, name='api_berita'),
    
]