from django.db import models
from django.contrib.auth.models import User

class Kategori(models.Model):
    nama = models.CharField(max_length=100)
    
    def __str__(self):
        return self.nama

class Artikel(models.Model):
    judul = models.CharField(max_length=255)
    konten = models.TextField()
    gambar_cover = models.ImageField(upload_to='berita/', null=True, blank=True)
    # TYPO DIPERBAIKI PADA BARIS DI BAWAH INI: on_delete=models.CASCADE
    kategori = models.ForeignKey(Kategori, on_delete=models.CASCADE)
    tanggal_publikasi = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.judul

class Komentar(models.Model):
    artikel = models.ForeignKey(Artikel, on_delete=models.CASCADE, related_name='komentar')
    nama_pengguna = models.CharField(max_length=100)
    isi_komentar = models.TextField()
    tanggal_dibuat = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Komentar oleh {self.nama_pengguna} di {self.artikel.judul}"