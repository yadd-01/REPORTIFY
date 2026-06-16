from django.shortcuts import render

# Create your views here.

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .services import tanya_deepseek, cek_hoaks_berita    # Mengambil fungsi dari services.py

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

@csrf_exempt 
def halaman_cek_fakta(request):
    if request.method == "GET":
        return render(request, 'cek_fakta.html')
    
    elif request.method == "POST":
        teks_input_user = request.POST.get('teks_berita', '').strip()
        
        if teks_input_user:
            try:
                hasil_ai = cek_hoaks_berita(teks_input_user)
                
                return JsonResponse({
                    'success': True,
                    'hasil_analisis': hasil_ai
                })
            except Exception as e:
                error_msg = str(e)
                if "429" in error_msg or "quota" in error_msg.lower():
                    pesan_custom = "Sistem AI sedang membatasi kuota gratis. Mohon tunggu sekitar 1 menit sebelum mengirim teks lagi."
                elif "503" in error_msg or "Service Unavailable" in error_msg:
                    pesan_custom = "Server Google Gemini sedang sibuk atau kelebihan beban (Eror 503). Mohon coba beberapa saat lagi."
                else:
                    pesan_custom = f"Gagal memproses AI: {error_msg}"

                return JsonResponse({
                    'success': False, 
                    'error': pesan_custom
                })
                
        return JsonResponse({
            'success': False, 
            'error': 'Teks berita tidak boleh kosong.'
        })