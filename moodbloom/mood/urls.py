from django.urls import path
from . import views

urlpatterns = [
    # 首页与登录
    path('', views.login_view, name='login'),
    
    # 身份验证相关
    path('register/', views.register_view, name='register'),
    path('logout/', views.user_logout, name='logout'),
    path('forgot/', views.forgot_view, name='forgot'),
    path('verify/<uidb64>/<token>/', views.verify_email, name='verify_email'), # 保留队友的邮箱验证
    
    # 核心主页与功能
    path('mainpage/', views.mainpage_view, name='mainpage'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('profile/', views.profile_view, name='profile'),
    path('moodentry/', views.moodentry_view, name='moodentry'),
    
    # 其他页面
    path('feedback/', views.feedback_view, name='feedback'),
    path('article/', views.article_view, name='article'),
    path('gallery/', views.gallery_view, name='gallery'),
    path('search/', views.search_view, name='search'),
]