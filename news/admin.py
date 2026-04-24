from django.contrib import admin
from .models import Kategori, Artikel

# Mendaftarkan model agar muncul di dashboard admin
admin.site.register(Kategori)
admin.site.register(Artikel)