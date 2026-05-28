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

    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"        
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