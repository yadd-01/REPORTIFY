from django import forms
from .models import Komentar, Artikel

class KomentarForm(forms.ModelForm):
    class Meta:
        model = Komentar
        fields = ['nama_pengguna', 'isi_komentar']
        widgets = {
            'nama_pengguna': forms.TextInput(attrs={'class': 'form-control rounded-pill ps-4', 'placeholder': 'Nama Anda...'}),
            'isi_komentar': forms.Textarea(attrs={'class': 'form-control rounded-4 ps-4 pt-3', 'placeholder': 'Tulis komentar...', 'rows': 3}),
        }

class ArtikelAdminForm(forms.ModelForm):
    class Meta:
        model = Artikel
        fields = ['judul', 'isi', 'gambar_cover', 'kategori']
        widgets = {
            'judul': forms.TextInput(attrs={'class': 'form-input-admin', 'placeholder': 'Masukkan judul berita...'}),
            # Field 'isi' di-handle oleh Quill.js di template, jadi widget-nya disembunyikan
            'isi': forms.HiddenInput(),
            'kategori': forms.Select(attrs={'class': 'form-input-admin'}),
        }