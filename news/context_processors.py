from .models import Kategori
from .views import hitung_trending_topics, buat_trending_gabungan

def news_global_context(request):
    """
    Context processor untuk menyediakan data kategori dan trending 
    ke seluruh halaman secara otomatis (termasuk halaman cek fakta, auth, dll).
    """
    # Jangan inject pada url admin Django bawaan atau admin-panel agar performa optimal
    if request.path.startswith('/admin/') or request.path.startswith('/admin-panel/'):
        return {}
        
    return {
        'daftar_kategori': Kategori.objects.all(),
        'topik_trending': hitung_trending_topics(),
        'daftar_trending_gabungan': buat_trending_gabungan(),
    }
