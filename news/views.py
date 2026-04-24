from django.shortcuts import render, get_object_or_404
from .models import Artikel
import requests

def beranda(request):
    # 1. Ambil berita lokal
    semua_berita_lokal = Artikel.objects.all().order_by('-tanggal_publikasi')
    
    # 2. Ambil berita API
    api_key = 'ab1b66225c8b4d14fe45c82bcb8bcbec'
    url = f"https://gnews.io/api/v4/top-headlines?category=general&lang=id&country=id&max=5&apikey={api_key}"
    
    berita_gnews = []
    pesan_error = "" # Wadah untuk menampung pesan error dari GNews
    
    try:
        response = requests.get(url)
        if response.status_code == 200: 
            data = response.json()
            berita_gnews = data.get('articles', [])
        else:
            # Menangkap pesan error asli dari GNews
            pesan_error = f"Error Code {response.status_code}: {response.text}"
    except Exception as e:
        pesan_error = f"Masalah koneksi server: {e}"

    # 3. Kirim semua data ke HTML
    context = {
        'berita_list': semua_berita_lokal,
        'berita_api': berita_gnews,
        'pesan_error': pesan_error, # Kita kirim errornya ke template
    }
    return render(request, 'beranda.html', context)

def detail_berita(request, artikel_id):
    artikel = get_object_or_404(Artikel, id=artikel_id)
    return render(request, 'detail_berita.html', {'berita': artikel})