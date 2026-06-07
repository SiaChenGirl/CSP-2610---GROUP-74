"""
URL configuration for users app.
本文件已完美整合网页模板渲染路由与核心后端 API 接口。
"""

from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # ==========================================
    # 1. 网页模板渲染路由 (负责让你和队友打开页面)
    # ==========================================
    path('', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.user_logout, name='logout'),
    path('forgot/', views.forgot_view, name='forgot'),
    
    path('mainpage/', views.mainpage_view, name='mainpage'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('profile/', views.profile_view, name='profile'),
    path('moodentry/', views.moodentry_view, name='moodentry'),
    path('article/', views.article_view, name='article'),
    path('gallery/', views.gallery_view, name='gallery'),
    path('search/', views.search_view, name='search'),
    path('feedback/', views.feedback_view, name='feedback'),

    # 🔗 【核心修复】在此处补齐文章方块跳转所需的路由名，100% 对应 article.html 的 href
    path('article/paragraph/', views.article_view, name='paragraph'),  
    path('article/favourite/', views.article_view, name='favourite'),  

    # ==========================================
    # 2. 核心后端核心 API 接口 (完全采用你们原有的体系)
    # ==========================================
    path('api/register/', views.register_view), # 已绑定你最新的合并注册逻辑
    path('login/', views.login_view, name='login_page'),     # 已绑定合并登录
    path('api/logout/', views.user_logout),
    path('api/profile/', views.profile_view),
    path('api/change-password/', views.change_password),
    
    # 邮件验证
    path('verify-email/<str:username>/', views.verify_email),

    # 心情数据存取
    path('add-mood/', views.moodentry_view),     # 完美兼容你之前的测试逻辑与新录入
    path('today-mood/', views.today_mood),
    path('search-entries/', views.search_view), # 绑定至高级合并搜索逻辑

    # 多媒体照片上传
    path('upload-photo/<int:entry_id>/', views.upload_photo),
    path('api/photo-gallery/', views.gallery_view),
    
    # 核心：心理健康文章与收藏夹 API (完美对接你的 article.html 点击加载分类)
    path('api/articles/', views.get_articles_by_category, name='api_articles'),
    path('api/favorite/<int:article_id>/', views.add_favorite),
    path('api/unfavorite/<int:article_id>/', views.remove_favorite),

    # 反馈系统 API
    path('api/feedback/', views.feedback_view),

    # 仪表盘打卡、图表数据 API
    path('api/dashboard-status/', views.dashboard_view),

    # ==========================================
    # 3. 密码重置官方内置路由 (保留原有高阶安全功能)
    # ==========================================
    path(
        'api/password-reset/',
        auth_views.PasswordResetView.as_view(),
        name='password_reset'
    ),
    path(
        'api/password-reset/done/',
         auth_views.PasswordResetDoneView.as_view(),
         name='password_reset_done'
    ),
    path(
        'api/reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(),
        name='password_reset_confirm'
    ),
    path(
        'api/reset/done/',
        auth_views.PasswordResetCompleteView.as_view(),
        name='password_reset_complete'
    ),
]