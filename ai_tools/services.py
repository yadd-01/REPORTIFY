import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()  # Memuat variabel lingkungan dari file .env

def tanya_deepseek(prompt_user, system_instruction):
    """
    Fungsi versi final menggunakan Google Gemini API.
    Format teks digabungkan langsung agar kompatibel 100% dengan endpoint v1 dan v1beta 
    tanpa memicu eror 'Unknown name systemInstruction'.
    """

    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"        
    headers = {
        'Content-Type': 'application/json'
    }
    

    konteks_lengkap = (
        f"Kamu adalah chatbot untuk aplikasi Report.Hub. Aturan karaktermu: {str(system_instruction)}\n"
        f"ATURAN GAYA BICARA:\n"
        f"1. JANGAN PERNAH gunakan kata sapaan seperti 'Halo!', 'Hai!', 'Selamat pagi/siang/malam' jika pengguna langsung bertanya atau melanjutkan percakapan.\n"
        f"2. Langsung jawab pertanyaan pengguna ke inti masalah dengan padat, informatif, dan jelas.\n"
        f"3. Jangan gunakan format Markdown seperti tanda bintang (** atau *).\n\n"
        f"Pertanyaan pengguna: {str(prompt_user)}"
    )
    
    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": konteks_lengkap
                    }
                ]
            }
        ]
    }
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        
        if response.status_code == 200:
            data = response.json()

            jawaban_ai = data['candidates'][0]['content']['parts'][0]['text']
            return jawaban_ai
        else:
            try:
                pesan_eror = response.json().get('error', {}).get('message', 'Gagal mendapatkan jawaban.')
                return f"Eror Sistem AI (Status {response.status_code}): {pesan_eror}"
            except:
                return f"Eror Sistem AI (Status {response.status_code}): Server Google menolak request."
            
    except Exception as e:
        return f"Koneksi terputus: {str(e)}"

def cek_hoaks_berita(teks_berita_user):
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {'Content-Type': 'application/json'}
    
    system_instruction = (
        "Kamu adalah AI Ahli Cek Fakta (Fact-Checker) profesional di portal Report.Hub. "
        "Tugasmu adalah menganalisis teks berita yang diberikan pengguna secara kritis untuk mendeteksi HOAKS, DISINFORMASI, atau KLIKBAIT.\n\n"
        "Aturan Jawaban:\n"
        "1. Di baris pertama wajib berikan kesimpulan tegas beserta persentase estimasi, contoh: [ANALISIS: 80% BERPOTENSI HOAKS] atau [ANALISIS: 90% VALID].\n"
        "2. Di baris berikutnya, berikan maksimal 3-4 poin alasan logis kenapa kamu memberikan penilaian tersebut (analisis dari judul, bahasa hiperbola, atau ketiadaan sumber primer).\n"
        "3. Gunakan bahasa yang tegas, padat, dan JANGAN gunakan format bintang-bintang (**) untuk menebalkan teks."
    )
    
    konteks_lengkap = f"{system_instruction}\n\nTeks berita:\n{teks_berita_user}"
    payload = {"contents": [{"parts": [{"text": konteks_lengkap}]}]}
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        if response.status_code == 200:
            return response.json()['candidates'][0]['content']['parts'][0]['text']
        return f"Eror Sistem AI ({response.status_code})"
    except Exception as e:
        return f"Koneksi terputus: {str(e)}"