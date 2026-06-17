import os
import time
import requests
import json
from dotenv import load_dotenv

load_dotenv()  # Memuat variabel lingkungan dari file .env

# Model Gemini yang digunakan — ganti di satu tempat ini saja
GEMINI_MODEL = "gemini-2.0-flash"

def _panggil_gemini(teks_prompt, max_retry=2):
    """
    Helper internal: panggil Gemini API dengan retry otomatis saat kena 429.
    max_retry = jumlah percobaan ulang setelah gagal (default 2x).
    """
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

    if not GEMINI_API_KEY:
        return None, "GEMINI_API_KEY tidak ditemukan. Pastikan sudah diset di environment variable."

    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
    )
    headers = {'Content-Type': 'application/json'}
    payload = {"contents": [{"parts": [{"text": teks_prompt}]}]}

    for percobaan in range(max_retry + 1):
        try:
            response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=30)

            if response.status_code == 200:
                data = response.json()
                teks = data['candidates'][0]['content']['parts'][0]['text']
                return teks, None

            elif response.status_code == 429:
                # Rate limit — coba baca berapa detik harus tunggu dari pesan error
                try:
                    pesan = response.json().get('error', {}).get('message', '')
                except Exception:
                    pesan = ''

                # Coba ekstrak waktu tunggu dari pesan, default 15 detik
                tunggu = 15
                import re
                cocok = re.search(r'retry in (\d+)', pesan, re.IGNORECASE)
                if cocok:
                    tunggu = int(cocok.group(1)) + 2  # tambah 2 detik buffer

                if percobaan < max_retry:
                    time.sleep(tunggu)
                    continue  # coba lagi
                else:
                    return None, (
                        "Server AI sedang sibuk (terlalu banyak permintaan). "
                        "Mohon tunggu sekitar 1 menit lalu coba lagi."
                    )

            elif response.status_code == 503:
                if percobaan < max_retry:
                    time.sleep(10)
                    continue
                return None, "Server Google Gemini sedang tidak tersedia (503). Coba beberapa saat lagi."

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
            return None, "Koneksi ke server AI timeout. Periksa koneksi internet dan coba lagi."
        except Exception as e:
            return None, f"Koneksi terputus: {str(e)}"

    return None, "Gagal menghubungi server AI setelah beberapa percobaan."


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