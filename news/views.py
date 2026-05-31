from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.db.models import Q
import requests

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

@api_view(['GET'])
def api_berita(request):
    semua_berita = Artikel.objects.all().order_by('-tanggal_publikasi')
    penerjemah = ArtikelSerializer(semua_berita, many=True)
    return Response(penerjemah.data)

def beranda(request):
    query = request.GET.get('q')
    kategori_filter = request.GET.get('kategori')
    
    semua_berita_lokal = Artikel.objects.all().order_by('-tanggal_publikasi')

    # PERBAIKAN: Diubah menjadi isi__icontains agar sinkron dengan model
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

    context = {
        'page_obj': page_obj,
        'berita_api': berita_gnews,
        'daftar_kategori': daftar_kategori,
        'pesan_error': pesan_error,
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
            if request.user.is_authenticated and not komentar_baru.nama:
                komentar_baru.nama = request.user.username
            komentar_baru.save()
            return redirect('detail_berita', artikel_id=artikel.id)
    else:
        form = KomentarForm()

    context = {
        'berita': artikel,
        'daftar_komentar': daftar_komentar,
        'form': form,
        'daftar_kategori': daftar_kategori,
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