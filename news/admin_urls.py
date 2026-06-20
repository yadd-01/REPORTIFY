from django.urls import path
from . import admin_views

urlpatterns = [
    # Dashboard
    path('', admin_views.admin_dashboard, name='admin_dashboard'),

    # News / Artikel
    path('news/', admin_views.admin_news, name='admin_news'),
    path('news/create/', admin_views.admin_article_create, name='admin_article_create'),
    path('news/<int:artikel_id>/edit/', admin_views.admin_article_edit, name='admin_article_edit'),
    path('news/<int:artikel_id>/delete/', admin_views.admin_article_delete, name='admin_article_delete'),

    # Categories (INI YANG SEBELUMNYA TERLEWAT)
    path('categories/', admin_views.admin_categories, name='admin_categories'),
    path('categories/create/', admin_views.admin_category_create, name='admin_category_create'),
    path('categories/<int:kat_id>/edit/', admin_views.admin_category_edit, name='admin_category_edit'),
    path('categories/<int:kat_id>/delete/', admin_views.admin_category_delete, name='admin_category_delete'),

    # Lain-lain
    path('users/', admin_views.admin_users, name='admin_users'),
    path('users/<int:user_id>/delete/', admin_views.admin_user_delete, name='admin_user_delete'),
    path('reports/', admin_views.admin_reports, name='admin_reports'),
    path('ai-summary/', admin_views.admin_ai_summary, name='admin_ai_summary'),
]