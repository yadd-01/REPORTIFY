import requests

def tanya_deepseek(prompt_user, system_instruction):
    """
    Fungsi untuk mengirim pertanyaan ke DeepSeek API 
    menggunakan konfigurasi token langsung dari dosen.
    """
    url = "https://api.deepseek.com/chat/completions"
    
    api_key = "sk-df07db4db82f4045ab245d78cf884cb8"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": prompt_user}
        ],
        "stream": False
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            return data["choices"][0]["message"]["content"]
        else:
            return f"Error: Gagal mendapatkan respon dari server AI (Status {response.status_code})."
            
    except requests.exceptions.RequestException as e:
        return f"Error Koneksi: {str(e)}"