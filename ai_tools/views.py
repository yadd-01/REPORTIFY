from django.shortcuts import render

# Create your views here.

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .services import tanya_deepseek  # Mengambil fungsi dari services.py

@csrf_exempt
def api_tanya_ai(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_message = data.get("message", "") 
            
            if not user_message:
                return JsonResponse({"status": "error", "reply": "Pesan tidak boleh kosong"}, status=400)
            
            instruksi_sistem = (
                "Kamu adalah Asisten AI resmi untuk portal berita bernama Report.Hub. "
                "Tugas utamanya adalah menjawab pertanyaan seputar berita, membantu merangkum "
                "artikel berita yang panjang menjadi poin ringkas (TL;DR), atau memberikan rekomendasi "
                "topik berita yang sedang trending. Jawablah dengan bahasa Indonesia yang ramah, "
                "profesional, dan ringkas."
            )
            
            # memanggil fungsi dari service.py
            jawaban_ai = tanya_deepseek(
                prompt_user=user_message,
                system_instruction=instruksi_sistem
            )
            
            # Mengembalikan response sukses
            return JsonResponse({"status": "success", "reply": jawaban_ai})
            
        except Exception as e:
            return JsonResponse({"status": "error", "reply": f"Kendala internal: {str(e)}"}, status=500)
            
    return JsonResponse({"status": "error", "reply": "Method tidak diizinkan"}, status=405)