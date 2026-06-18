from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.db.models import Q, Count, F
from django.core.cache import cache
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
# HELPER: AMBIL BERITA GNEWS
# =====================================================================
GNEWS_API_KEY = 'ab1b66225c8b4d14fe45c82bcb8bcbec'

def ambil_berita_gnews(max_hasil=5):
    """Ambil berita dari GNews API, return list artikel atau list kosong jika gagal (dengan caching)."""
    cache_key = f"gnews_articles_{max_hasil}"
    hasil_cached = cache.get(cache_key)
    if hasil_cached is not None:
        return hasil_cached

    url = (
        f"https://gnews.io/api/v4/top-headlines"
        f"?category=general&lang=id&country=id&max={max_hasil}&apikey={GNEWS_API_KEY}"
    )
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            articles = response.json().get('articles', [])
            cache.set(cache_key, articles, 600)  # Cache selama 10 menit
            return articles
    except Exception:
        pass
    return []


# =====================================================================
# HELPER: BUAT DAFTAR TRENDING GABUNGAN (LOKAL + GNEWS)
# =====================================================================
def buat_trending_gabungan(berita_gnews=None):
    """
    Gabungkan berita lokal (diurutkan views terbanyak) dengan berita GNews
    menjadi satu daftar trending tanpa pembeda.
    Setiap item punya: judul, url, gambar, sumber, views (None untuk GNews)
    """
    trending = []

    # 1. Berita lokal — ambil 5 terbanyak views
    berita_lokal_top = Artikel.objects.order_by('-jumlah_views', '-tanggal_publikasi')[:5]
    for artikel in berita_lokal_top:
        gambar_url = artikel.gambar_cover.url if artikel.gambar_cover else None
        trending.append({
            'judul': artikel.judul,
            'url': f'/berita/{artikel.id}/',   # url internal
            'gambar': gambar_url,
            'sumber': 'Report.Hub',
            'views': artikel.jumlah_views,
            'is_lokal': True,
            'artikel_id': artikel.id,
        })

    # 2. Berita GNews — pakai data yang sudah diambil (hindari request dobel)
    if berita_gnews is None:
        berita_gnews = ambil_berita_gnews(max_hasil=5)

    for gnews in berita_gnews:
        trending.append({
            'judul': gnews.get('title', ''),
            'url': gnews.get('url', '#'),
            'gambar': gnews.get('image', ''),
            'sumber': gnews.get('source', {}).get('name', 'GNews'),
            'views': None,   # GNews tidak punya views
            'is_lokal': False,
            'artikel_id': None,
        })

    # 3. Urutkan: lokal (punya views) diutamakan, lalu campur dengan GNews
    #    Lokal diurut by views desc, GNews menyusul di belakang
    lokal = [t for t in trending if t['is_lokal']]
    gnews_list = [t for t in trending if not t['is_lokal']]

    # Gabung: lokal dulu (sudah urut views), lalu gnews
    hasil_gabung = lokal + gnews_list

    # Batasi tampil maksimal 8 item
    return hasil_gabung[:8]


# =====================================================================
# MESIN SISTEM PAKAR: DETEKSI TOPIK TRENDING DINAMIS (RULE-BASED HYBRID)
# =====================================================================
def hitung_trending_topics():
    STOPWORDS = set([
        'yang', 'di', 'ke', 'dari', 'adalah', 'dan', 'atau', 'ini', 'itu', 'dengan',
        'untuk', 'pada', 'bahwa', 'oleh', 'juga', 'telah', 'sudah', 'akan', 'bisa',
        'dapat', 'ada', 'dari', 'dalam', 'secara', 'tersebut', 'dia', 'mereka', 'kami',
        'kita', 'saya', 'kamu', 'seperti', 'oleh', 'karena', 'namun', 'melainkan'
    ])

    semua_artikel = Artikel.objects.annotate(total_komentar=Count('komentar'))
    kamus_topik = {}

    for artikel in semua_artikel:
        teks_bersih = re.sub(r'<[^>]+>', '', (artikel.judul + " " + artikel.isi).lower())
        kata_kata = re.findall(r'\b[a-z]{4,20}\b', teks_bersih)
        bobot_interaksi = artikel.total_komentar * 2

        for kata in kata_kata:
            if kata not in STOPWORDS:
                kamus_topik[kata] = kamus_topik.get(kata, 0) + (1 + bobot_interaksi)

    topik_terurut = sorted(kamus_topik.items(), key=lambda x: x[1], reverse=True)
    daftar_trending = [topik[0].capitalize() for topik in topik_terurut[:5]]

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

    paginator = Paginator(semua_berita_lokal, 4)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Ambil GNews untuk sidebar GNews Live
    berita_gnews = ambil_berita_gnews(max_hasil=5)

    context = {
        'page_obj': page_obj,
        'berita_api': berita_gnews,
    }
    return render(request, 'beranda.html', context)

def detail_berita(request, artikel_id):
    artikel = get_object_or_404(Artikel, id=artikel_id)

    # Tambah view count setiap kali halaman dibuka (F() untuk atomic update)
    Artikel.objects.filter(id=artikel_id).update(jumlah_views=F('jumlah_views') + 1)

    daftar_komentar = artikel.komentar.all().order_by('-tanggal_dibuat')

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

    context = {
        'berita': artikel,
        'daftar_komentar': daftar_komentar,
        'form': form,
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