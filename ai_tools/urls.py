from django.urls import path
from . import views

urlpatterns = [
    path('api/v1/ai-chat/', views.api_tanya_ai, name='api_tanya_ai'),
    path('cek-fakta/', views.halaman_cek_fakta, name='cek_fakta'),
]