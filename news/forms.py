from django import forms
from .models import Komentar

class KomentarForm(forms.ModelForm):
    class Meta:
        model = Komentar
        fields = ['nama_pengguna', 'isi_komentar']
        widgets = {
            'nama_pengguna': forms.TextInput(attrs={
                'class': 'form-control rounded-pill ps-4',
                'placeholder': 'Masukkan Nama Anda...'
            }),
            'isi_komentar': forms.Textarea(attrs={
                'class': 'form-control rounded-4 ps-4 pt-3',
                'placeholder': 'Tulis komentar Anda di sini...',
                'rows': 3
            }),
        }