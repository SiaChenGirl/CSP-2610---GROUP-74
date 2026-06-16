from django.urls import path
from . import views

urlpatterns = [
    # ==========================================
    # 1. 网页模板渲染路由 (页面导航)
    # ==========================================
    path('', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.user_logout, name='logout'),
    path('mainpage/', views.mainpage_view, name='mainpage'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('profile/', views.profile_view, name='profile'),
    path('moodentry/', views.moodentry_view, name='moodentry'),
    path('article/', views.article_view, name='article'),
    path('article/paragraph/', views.paragraph_view, name='paragraph'),
    path('article/favourite/', views.favourite_page_view, name='favourite'),
    path('gallery/', views.gallery_view, name='gallery'),
    path('search/', views.search_view, name='search'),
    path('feedback/', views.feedback_view, name='feedback'),

    # ==========================================
    # 2. 核心后端 API 接口
    # ==========================================
    path('api/register/', views.register_view),
    path('api/logout/', views.user_logout),
    path('api/profile/', views.profile_view),
    path('api/change-password/', views.change_password),
    path('verify-email/<str:username>/', views.verify_email, name='verify_email'),
    path('add-mood/', views.moodentry_view),
    path('today-mood/', views.today_mood),
    path('search-entries/', views.search_view),
    path('upload-photo/<int:entry_id>/', views.upload_photo),
    path('api/photo-gallery/', views.gallery_view),
    path('api/articles/', views.get_articles_by_category, name='api_articles'),
    path('api/favorite/<int:article_id>/', views.add_favorite),
    path('api/unfavorite/<int:article_id>/', views.remove_favorite),
    path('api/feedback/', views.feedback_view),
    path('api/dashboard-status/', views.dashboard_view),
    path('api/music-library/', views.get_music_library),
    path('api/articles/favorite/<int:article_id>/', views.toggle_favorite, name='toggle_favorite'),
   path('search/', views.search_view, name='search'),
    # ==========================================
    # 3. 密码重置专用路由 (核心修复区)
    # ==========================================
    # 这里的 'forgot/' 指向发送邮件的逻辑
    path('forgot/', views.forgot_password_action, name='forgot'),
    
    # 用户点邮件里的链接跳转到这里
    path('reset/<uidb64>/<token>/', views.custom_reset_view, name='password_reset_confirm'),
    
    # reset.html 提交保存密码的接口
    path('reset-save/', views.handle_password_save, name='password_reset_save'),

    # ... 在 api/favorite/ 下方补上：
    path('remove-favorite/<int:article_id>/', views.remove_favorite, name='remove_favorite'),
]