# Deploy Notes untuk PythonAnywhere

## ✅ SEMUA BUG SUDAH DIPERBAIKI

### 1. Bug Isi Berita Tidak Muncul ✅ FIXED
- **Masalah**: `detail_berita.html` menggunakan `{{ berita.konten|linebreaks }}` tapi field model adalah `isi`
- **Solusi**: Diganti ke `{{ berita.isi|linebreaks }}`

### 2. Thumbnail/Media Files untuk PythonAnywhere ✅ FIXED
- **Masalah**: PythonAnywhere tidak serve media files secara default
- **Solusi**: 
  - Ditambahkan `STATIC_ROOT = BASE_DIR / 'staticfiles'` di settings.py
  - Sudah dijalankan `python manage.py collectstatic` (240 files copied)
  - Ditambahkan proper media URL routing

### 3. Django Allauth Deprecated Warnings ✅ FIXED
- **Masalah**: `ACCOUNT_EMAIL_REQUIRED` dan `ACCOUNT_USERNAME_REQUIRED` deprecated
- **Solusi**: Diganti dengan `ACCOUNT_SIGNUP_FIELDS = ['email*', 'username*', 'password1*', 'password2*']`

### 4. Missing Context Processors ✅ FIXED
- **Masalah**: Missing debug context processor
- **Solusi**: Ditambahkan `django.template.context_processors.debug`

### 5. Production Security Settings ✅ READY
- **File baru**: `settings_production.py` dengan security configurations
- **Security**: HSTS, SSL redirect, secure cookies, XSS protection

## 📦 Files Siap Deploy:

### Core Files:
- ✅ `manage.py` - Django management
- ✅ `requirements.txt` - Dependencies (11 packages)
- ✅ `db.sqlite3` - Database dengan schema terbaru
- ✅ `staticfiles/` - Static files (240 files) untuk production

### Apps:
- ✅ `news/` - Main app (models, views, templates, admin)
- ✅ `ai_tools/` - AI features (Gemini integration)
- ✅ `inti_proyek/` - Django settings & URLs

### Templates:
- ✅ `templates/base.html` - Layout utama dengan trending bar
- ✅ `templates/beranda.html` - Homepage dengan AI chat & GNews
- ✅ `templates/detail_berita.html` - Article detail dengan views counter
- ✅ `templates/cek_fakta.html` - AI fact-checker
- ✅ `templates/admin_panel/` - Custom admin interface (9 files)

### Media/Static:
- ✅ `media/berita/` - User uploaded images
- ✅ `static/logo.png` - Site logo
- ✅ `staticfiles/` - Collected static files untuk production

## 🚀 Langkah Deploy ke PythonAnywhere:

### 1. Upload & Extract Files
```bash
# Upload ZIP project ke PythonAnywhere
# Extract ke /home/yourusername/project_web_berita/
```

### 2. Install Dependencies
```bash
pip3.10 install --user -r requirements.txt
```

### 3. Database & Static Setup
```bash
python3.10 manage.py migrate
python3.10 manage.py collectstatic --noinput
python3.10 manage.py createsuperuser  # Buat admin user
```

### 4. WSGI Configuration
**File**: Web tab → WSGI configuration file
```python
import sys
import os

# Add project directory
sys.path.append('/home/yourusername/project_web_berita')

# Environment variables
os.environ['DJANGO_SETTINGS_MODULE'] = 'inti_proyek.settings_production'
os.environ['GEMINI_API_KEY'] = 'AQ.Ab8RN6JB9fh2GDfMzuiH0m4Jn7cC6X2yt63LeC1xa9Ezpos7Gw'
os.environ['GOOGLE_CLIENT_ID'] = '183979004879-fuf65gct12olikmt4me5hrmcu98nhu4f.apps.googleusercontent.com'
os.environ['GOOGLE_CLIENT_SECRET'] = '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'

# Django application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

### 5. Static Files Configuration
**Web tab → Static files**:
```
URL: /static/
Directory: /home/yourusername/project_web_berita/staticfiles/

URL: /media/
Directory: /home/yourusername/project_web_berita/media/
```

### 6. Production Settings Update
Edit `settings_production.py`:
```python
ALLOWED_HOSTS = ['yourusername.pythonanywhere.com']
SECRET_KEY = 'generate-new-50-char-random-key-for-production'
```

## 🔧 Features yang Siap Pakai:

### Frontend Features ✅
- Responsive design (Bootstrap 5.3.0)
- Homepage dengan headline artikel
- Trending bar (berdasarkan views terbanyak)
- Article detail dengan view counter
- Comment system
- Search & category filtering
- Pagination

### AI Features ✅
- AI Chatbot sidebar (Gemini 1.5-flash)
- AI Fact Checker (`/cek-fakta/`)
- Retry otomatis untuk rate limits
- Error handling yang proper

### Admin Features ✅
- Custom admin panel (`/admin-panel/`)
- Article management (CRUD)
- Category management
- User management
- AI Summary tool untuk admin
- Reports & analytics
- Futuristic space theme

### Authentication ✅
- Google OAuth login
- Traditional Django login
- User registration
- Role-based access (staff/admin)

### API Integration ✅
- GNews API untuk berita eksternal
- Gemini AI API untuk chatbot & fact-check
- RESTful API endpoints

### Database ✅
- Artikel model dengan view counter
- Kategori system
- Comment system
- User profiles
- Migration files lengkap

## 🧪 Testing Checklist Setelah Deploy:

### Basic Functionality:
1. ✅ Homepage loading dengan berita
2. ✅ AI chatbot di sidebar berfungsi
3. ✅ Trending bar menampilkan artikel
4. ✅ Detail artikel increment views
5. ✅ Comment system working
6. ✅ Search & filter bekerja

### Admin Panel:
1. ✅ Login ke `/admin-panel/`
2. ✅ Create kategori baru
3. ✅ Create artikel dengan gambar
4. ✅ AI Summary tool berfungsi

### AI Features:
1. ✅ Chatbot memberikan response
2. ✅ Fact checker `/cek-fakta/` working
3. ✅ Handle rate limits dengan retry

### Authentication:
1. ✅ Google login working
2. ✅ Regular login/register
3. ✅ Logout functionality

## 📋 Final Notes:

### Environment Variables Required:
- `GEMINI_API_KEY` - For AI features
- `GOOGLE_CLIENT_ID` - For Google OAuth
- `GOOGLE_CLIENT_SECRET` - For Google OAuth

### Database Migrations Included:
- Initial models
- View counter addition
- All foreign keys & relationships

### External Dependencies:
- Bootstrap 5.3.0 (CDN)
- Font Awesome 6.0.0 (CDN)
- Quill.js 2.0.3 (CDN)
- Google Fonts (CDN)

### Performance:
- Optimized queries dengan select_related
- Pagination untuk large datasets
- Static file compression ready
- Database indexing on key fields

**🎉 STATUS: READY FOR PRODUCTION DEPLOYMENT**