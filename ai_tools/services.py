import os
import time
import requests
import json
from dotenv import load_dotenv

load_dotenv()  # Memuat variabel lingkungan dari file .env

# Model Gemini yang digunakan — ganti di satu tempat ini saja
# gemini-1.5-flash lebih stabil, fallback ke gemini-2.0-flash jika 503
GEMINI_MODEL = "gemini-1.5-flash"
GEMINI_MODEL_FALLBACK = "gemini-2.0-flash"

def _panggil_gemini(teks_prompt, max_retry=2):
    """
    Helper internal: panggil Gemini API dengan retry otomatis saat kena 429/503.
    Jika model utama 503, otomatis fallback ke model cadangan.
    """
    import re
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    GEMINI_BASE_URL = os.getenv("GEMINI_BASE_URL")

    if not GEMINI_API_KEY:
        return None, "GEMINI_API_KEY tidak ditemukan. Pastikan sudah diset di environment variable."


    headers = {'Content-Type': 'application/json'}
    payload = {"contents": [{"parts": [{"text": teks_prompt}]}]}

    # Coba model utama dulu, lalu fallback jika 503
    daftar_model = [GEMINI_MODEL, GEMINI_MODEL_FALLBACK]

    for model in daftar_model:
        if GEMINI_BASE_URL:
            url = f"{GEMINI_BASE_URL}{GEMINI_API_KEY}"
        else:
            url = (
                f"https://generativelanguage.googleapis.com/v1beta/models/"
                f"{model}:generateContent?key={GEMINI_API_KEY}"
            )

        for percobaan in range(max_retry + 1):
            try:
                response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=30)

                if response.status_code == 200:
                    data = response.json()
                    teks = data['candidates'][0]['content']['parts'][0]['text']
                    return teks, None

                elif response.status_code == 429:
                    try:
                        pesan = response.json().get('error', {}).get('message', '')
                    except Exception:
                        pesan = ''

                    tunggu = 15
                    cocok = re.search(r'retry in (\d+)', pesan, re.IGNORECASE)
                    if cocok:
                        tunggu = int(cocok.group(1)) + 2

                    if percobaan < max_retry:
                        time.sleep(tunggu)
                        continue
                    else:
                        return None, (
                            "Server AI sedang sibuk (terlalu banyak permintaan). "
                            "Mohon tunggu sekitar 1 menit lalu coba lagi."
                        )

                elif response.status_code == 503:
                    # Model ini overload, retry dulu lalu fallback ke model lain
                    if percobaan < max_retry:
                        time.sleep(5)
                        continue
                    break  # keluar, coba model fallback

                else:
                    try:
                        pesan_eror = response.json().get('error', {}).get('message', 'Gagal mendapatkan jawaban.')
                    except Exception:
                        pesan_eror = f"Status {response.status_code}"
                    return None, f"Eror API ({response.status_code}): {pesan_eror}"

            except requests.exceptions.Timeout:
                if percobaan < max_retry:
                    time.sleep(5)
                    continue
                break  # coba model berikutnya
            except Exception as e:
                return None, f"Koneksi terputus: {str(e)}"

    return None, (
        "Semua model AI sedang mengalami gangguan. "
        "Ini biasanya sementara — mohon coba lagi dalam beberapa menit."
    )


def tanya_deepseek(prompt_user, system_instruction):
    """
    Fungsi utama chatbot menggunakan Google Gemini API.
    """
    konteks_lengkap = (
        f"Kamu adalah chatbot untuk aplikasi Report.Hub. Aturan karaktermu: {str(system_instruction)}\n"
        f"ATURAN GAYA BICARA:\n"
        f"1. JANGAN PERNAH gunakan kata sapaan seperti 'Halo!', 'Hai!', 'Selamat pagi/siang/malam' "
        f"jika pengguna langsung bertanya atau melanjutkan percakapan.\n"
        f"2. Langsung jawab pertanyaan pengguna ke inti masalah dengan padat, informatif, dan jelas.\n"
        f"3. Jangan gunakan format Markdown seperti tanda bintang (** atau *).\n\n"
        f"Pertanyaan pengguna: {str(prompt_user)}"
    )

    hasil, eror = _panggil_gemini(konteks_lengkap)
    if eror:
        return f"Eror Sistem AI: {eror}"
    return hasil


def cek_hoaks_berita(teks_berita_user):
    """
    Fungsi cek fakta / hoaks menggunakan Google Gemini API.
    """
    system_instruction = (
        "Kamu adalah AI Ahli Cek Fakta (Fact-Checker) profesional di portal Report.Hub. "
        "Tugasmu adalah menganalisis teks berita yang diberikan pengguna secara kritis "
        "untuk mendeteksi HOAKS, DISINFORMASI, atau KLIKBAIT.\n\n"
        "Aturan Jawaban:\n"
        "1. Di baris pertama wajib berikan kesimpulan tegas beserta persentase estimasi, "
        "contoh: [ANALISIS: 80% BERPOTENSI HOAKS] atau [ANALISIS: 90% VALID].\n"
        "2. Di baris berikutnya, berikan maksimal 3-4 poin alasan logis kenapa kamu memberikan "
        "penilaian tersebut (analisis dari judul, bahasa hiperbola, atau ketiadaan sumber primer).\n"
        "3. Gunakan bahasa yang tegas, padat, dan JANGAN gunakan format bintang-bintang (**) "
        "untuk menebalkan teks."
    )

    konteks_lengkap = f"{system_instruction}\n\nTeks berita:\n{teks_berita_user}"

    hasil, eror = _panggil_gemini(konteks_lengkap)
    if eror:
        raise Exception(eror)
    return hasil