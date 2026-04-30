from rest_framework import serializers
from .models import Artikel, Kategori

# Penerjemah untuk model Artikel
class ArtikelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Artikel
        fields = '__all__' 