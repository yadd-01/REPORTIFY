from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from .models import Artikel, Kategori
from .forms import ArtikelAdminForm
from django.db.models import Q

def is_staff(user):
    return user.is_authenticated and user.is_staff

staff_required = user_passes_test(is_staff, login_url='/accounts/login/')

def get_velocity_data():
    today = timezone.now().date()
    days = ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN']
    result = []
    max_count = 1
    counts = []
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        count = Artikel.objects.filter(tanggal_publikasi__date=day).count()
        counts.append({'date': day, 'count': count, 'label': days[day.weekday()]})
        if count > max_count: max_count = count
    for idx, item in enumerate(counts):
        height = max(4, int((item['count'] / max_count) * 80))
        result.append({'label': 'TODAY' if idx == len(counts) - 1 else item['label'], 'height': f"{height}%", 'count': item['count']})
    return result

@login_required
@staff_required
def admin_dashboard(request):
    context = {
        'total_articles': Artikel.objects.count(),
        'total_users': User.objects.count(),
        'recent_articles': Artikel.objects.order_by('-tanggal_publikasi')[:5],
        'total_users': User.objects.count(),
        'recent_users': User.objects.all().order_by('-last_login')[:5],
        'velocity': get_velocity_data(),
        'weekly_total': Artikel.objects.filter(tanggal_publikasi__gte=timezone.now() - timedelta(days=7)).count(),
        'kategori_stats': Kategori.objects.all(),
    }
    return render(request, 'admin_panel/dashboard.html', context)

@login_required
@staff_required
def admin_news(request):
    query = request.GET.get('q')
    if query:
        articles = Artikel.objects.filter(judul__icontains=query).order_by('-tanggal_publikasi')
    else:
        articles = Artikel.objects.all().order_by('-tanggal_publikasi')
    return render(request, 'admin_panel/admin_news.html', {'page_obj': articles})


@login_required
@staff_required
def admin_article_create(request):
    if request.method == 'POST':
        form = ArtikelAdminForm(request.POST, request.FILES)
        if form.is_valid():
            artikel = form.save(commit=False)
            artikel.penulis = request.user
            artikel.save()
            return redirect('admin_news')
    else:
        form = ArtikelAdminForm()
        
    
    daftar_kategori = Kategori.objects.all()
    
    return render(request, 'admin_panel/admin_article_form.html', {
        'form': form,
        'daftar_kategori': daftar_kategori  # Kirim ke template HTML
    })

@login_required
@staff_required
def admin_article_edit(request, artikel_id):
    artikel = get_object_or_404(Artikel, id=artikel_id)
    if request.method == 'POST':
        form = ArtikelAdminForm(request.POST, request.FILES, instance=artikel)
        if form.is_valid():
            form.save()
            return redirect('admin_news')
    else:
        form = ArtikelAdminForm(instance=artikel)
        
    
    daftar_kategori = Kategori.objects.all()
        
    return render(request, 'admin_panel/admin_article_form.html', {
        'form': form, 
        'artikel': artikel,
        'daftar_kategori': daftar_kategori  
    })

@login_required
@staff_required
def admin_article_delete(request, artikel_id):
    artikel = get_object_or_404(Artikel, id=artikel_id)
    if request.method == 'POST':
        artikel.delete()
        return redirect('admin_news')
    return render(request, 'admin_panel/admin_article_confirm_delete.html', {'artikel': artikel})

# ====================================================
# FUNGSI KATEGORI (BARU DITAMBAHKAN)
# ====================================================
@login_required
@staff_required
def admin_categories(request):
    if request.method == 'POST':
        nama = request.POST.get('nama', '').strip()
        if nama:
            Kategori.objects.create(nama=nama)
        return redirect('admin_categories')
        
    kategori = Kategori.objects.all()
    return render(request, 'admin_panel/admin_categories.html', {'daftar_kategori': kategori})

@login_required
@staff_required
def admin_category_create(request):
    # Form Tambah Kategori ada di dalam halaman yang sama, jadi kita kembalikan saja
    return redirect('admin_categories')

@login_required
@staff_required
def admin_category_edit(request, kat_id):
    kategori = get_object_or_404(Kategori, id=kat_id)
    if request.method == 'POST':
        nama = request.POST.get('nama', '').strip()
        if nama:
            kategori.nama = nama
            kategori.save()
        return redirect('admin_categories')
        
    daftar_kategori = Kategori.objects.all()
    return render(request, 'admin_panel/admin_categories.html', {
        'daftar_kategori': daftar_kategori,
        'edit_kat': kategori
    })

@login_required
@staff_required
def admin_category_delete(request, kat_id):
    kategori = get_object_or_404(Kategori, id=kat_id)
    if request.method == 'POST':
        kategori.delete()
        return redirect('admin_categories')
    return render(request, 'admin_panel/admin_category_confirm_delete.html', {'kat': kategori})
# ====================================================


@login_required
@staff_required
def admin_users(request):
    query = request.GET.get('q')
    
    # Fitur Pencarian User
    if query:
        users = User.objects.filter(
            Q(username__icontains=query) | Q(email__icontains=query)
        ).order_by('-date_joined')
    else:
        users = User.objects.all().order_by('-date_joined')
        
    seven_days_ago = timezone.now() - timedelta(days=7)
    
    context = {
        'daftar_user': users, 
        'total_users': User.objects.count(),
        'total_staff': User.objects.filter(is_staff=True).count(),
        'total_regular': User.objects.filter(is_staff=False, is_superuser=False).count(),
        'new_users_week': User.objects.filter(date_joined__gte=seven_days_ago).count(),
    }
    return render(request, 'admin_panel/admin_users.html', context)

@login_required
@staff_required
def admin_reports(request):
    from django.db.models import Count
    today = timezone.now().date()
    context = {
        'total_this_month': Artikel.objects.filter(tanggal_publikasi__month=today.month).count(),
        'artikel_per_kat': Kategori.objects.annotate(jumlah=Count('artikel')),
        'artikel_komentar': Artikel.objects.annotate(jumlah_komentar=Count('komentar')).order_by('-jumlah_komentar')[:5],
    }
    return render(request, 'admin_panel/admin_reports.html', context)

@login_required
@staff_required
def admin_ai_summary(request):
    return render(request, 'admin_panel/admin_ai_summary.html')