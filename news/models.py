from django.db import models
from django.contrib.auth.models import User

# Model untuk Kategori Berita (Politik, Olahraga, Teknologi, dll)
class Kategori(models.Model):
    nama = models.CharField(max_length=100)

    def __str__(self):
        return self.nama

# Model untuk Artikel Berita
class Artikel(models.Model):
    judul = models.CharField(max_length=255)
    konten = models.TextField() # Isi berita lengkap
    gambar_cover = models.ImageField(upload_to='cover_berita/', blank=True, null=True)
    kategori = models.ForeignKey(Kategori, on_delete=models.CASCADE) # Relasi ke Kategori
    penulis = models.ForeignKey(User, on_delete=models.SET_NULL, null=True) # Relasi ke User Admin
    tanggal_publikasi = models.DateTimeField(auto_now_add=True) # Terisi otomatis saat berita dibuat

    def __str__(self):
        return self.judul