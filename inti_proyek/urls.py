from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Rute CKEditor upload
    path('ckeditor5/', include('django_ckeditor_5.urls')),

    # Rute aplikasi utama
    path('', include('news.urls')), 
    
    # Rute Allauth
    path('accounts/', include('allauth.urls')),
    
    # 💡 TAMBAHKAN BARIS INI: Menyambungkan semua rute admin kustom
    path('admin-panel/', include('news.admin_urls')), 
    
    # fitur ai
    path('', include('ai_tools.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)