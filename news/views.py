from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.db.models import Q, Count
import requests
import re

# Import untuk kebutuhan API
from rest_framework.decorators import api_view
from rest_framework.response import Response

# Import untuk kebutuhan Autentikasi (Login & Register)
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib import messages

# Import Models & Forms lokal
from .models import Artikel, Komentar, Kategori
from .serializers import ArtikelSerializer
from .forms import KomentarForm

# =====================================================================
# MESIN SISTEM PAKAR: DETEKSI TOPID TRENDING DINAMIS (RULE-BASED HYBRID)
# =====================================================================
def hitung_trending_topics():
    """
    Fungsi Sistem Pakar untuk menganalisis konten teks artikel manual,
    menyaring kata hubung, menghitung frekuensi, dan menggabungkannya
    dengan bobot interaksi jumlah komentar.
    """
    # 1. Daftar Kata Hubung (Stopwords) Bahasa Indonesia untuk dieliminasi oleh sistem
    STOPWORDS = set([
        'yang', 'di', 'ke', 'dari', 'adalah', 'dan', 'atau', 'ini', 'itu', 'dengan', 
        'untuk', 'pada', 'bahwa', 'oleh', 'juga', 'telah', 'sudah', 'akan', 'bisa', 
        'dapat', 'ada', 'dari', 'dalam', 'secara', 'tersebut', 'dia', 'mereka', 'kami',
        'kita', 'saya', 'kamu', 'seperti', 'oleh', 'karena', 'namun', 'melainkan'
    ])
    
    # 2. Ambil artikel lengkap dengan jumlah komentar bawaannya
    semua_artikel = Artikel.objects.annotate(total_komentar=Count('komentar'))
    
    kamus_topik = {}

    for artikel in semua_artikel:
        # Satukan judul dan isi berita, lalu bersihkan dari tag HTML & simbol
        teks_bersih = re.sub(r'<[^>]+>', '', (artikel.judul + " " + artikel.isi).lower())
        kata_kata = re.findall(r'\b[a-z]{4,20}\b', teks_bersih) # Ambil kata dengan panjang 4-20 karakter

        # 3. Proses Pembobotan Pakar per Kata
        # Rule: Jika kata bukan stopwords, berikan nilai dasar frekuensi kata (+1)
        # ditambah bonus bobot dari interaksi komentar (Jumlah Komentar * 2)
        bobot_interaksi = artikel.total_komentar * 2
        
        for kata in kata_kata:
            if kata not in STOPWORDS:
                if kata in kamus_topik:
                    kamus_topik[kata] += (1 + bobot_interaksi)
                else:
                    kamus_topik[kata] = (1 + bobot_interaksi)

    # 4. Urutkan kata dari bobot nilai yang paling tinggi (Trending Utama)
    topik_terurut = sorted(kamus_topik.items(), key=lambda x: x[1], reverse=True)
    
    # Ambil 5 kata teratas dengan konversi huruf kapital di awal kata
    daftar_trending = [topik[0].capitalize() for topik in topik_terurut[:5]]
    
    # Fallback/Cadangan jika database masih kosong kosong
    if not daftar_trending:
        daftar_trending = ["Nasional", "Politik", "Kesehatan", "Teknologi", "Olahraga"]
        
    return daftar_trending


# =====================================================================
# VIEWS UTAMA DJANGO
# =====================================================================

@api_view(['GET'])
def api_berita(request):
    semua_berita = Artikel.objects.all().order_by('-tanggal_publikasi')
    penerjemah = ArtikelSerializer(semua_berita, many=True)
    return Response(penerjemah.data)

def beranda(request):
    query = request.GET.get('q')
    kategori_filter = request.GET.get('kategori')
    
    semua_berita_lokal = Artikel.objects.all().order_by('-tanggal_publikasi')

    if query:
        semua_berita_lokal = semua_berita_lokal.filter(
            Q(judul__icontains=query) | Q(isi__icontains=query)
        )
    
    if kategori_filter:
        semua_berita_lokal = semua_berita_lokal.filter(kategori__nama=kategori_filter)

    paginator = Paginator(semua_berita_lokal, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    api_key = 'ab1b66225c8b4d14fe45c82bcb8bcbec'
    url = f"https://gnews.io/api/v4/top-headlines?category=general&lang=id&country=id&max=5&apikey={api_key}"
    
    berita_gnews = []
    pesan_error = ""
    try:
        response = requests.get(url)
        if response.status_code == 200: 
            data = response.json()
            berita_gnews = data.get('articles', [])
        else:
            pesan_error = f"Error {response.status_code}: {response.text}"
    except Exception as e:
        pesan_error = f"Error koneksi: {e}"

    daftar_kategori = Kategori.objects.all()
    
    # PANGGIL MESIN SISTEM PAKAR TRENDING
    topik_trending = hitung_trending_topics()

    context = {
        'page_obj': page_obj,
        'berita_api': berita_gnews,
        'daftar_kategori': daftar_kategori,
        'pesan_error': pesan_error,
        'topik_trending': topik_trending, # Mengirimkan hasil pakar ke template HTML
    }
    return render(request, 'beranda.html', context)

def detail_berita(request, artikel_id):
    artikel = get_object_or_404(Artikel, id=artikel_id)
    daftar_komentar = artikel.komentar.all().order_by('-tanggal_dibuat')
    daftar_kategori = Kategori.objects.all()
    
    if request.method == 'POST':
        form = KomentarForm(request.POST)
        if form.is_valid():
            komentar_baru = form.save(commit=False)
            komentar_baru.artikel = artikel
            if request.user.is_authenticated and not komentar_baru.nama_pengguna:
                komentar_baru.nama_pengguna = request.user.username
            komentar_baru.save()
            return redirect('detail_berita', artikel_id=artikel.id)
    else:
        form = KomentarForm()

    # PANGGIL JUGA DI HALAMAN DETAIL AGAR NAVBAR ATAS SAMA-SAMA UPDATE
    topik_trending = hitung_trending_topics()

    context = {
        'berita': artikel,
        'daftar_komentar': daftar_komentar,
        'form': form,
        'daftar_kategori': daftar_kategori,
        'topik_trending': topik_trending, # Dikirim ke detail_berita.html
    }
    return render(request, 'detail_berita.html', context)

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Selamat datang, {user.username}! Akun Anda berhasil dibuat.")
            return redirect('beranda')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})