from django.urls import path
from . import views

urlpatterns = [
<<<<<<< HEAD
    path('', views.login_view, name='login'),      # 首页
    path('register/', views.register, name='register'), # 注册页
    path('dashboard/', views.dashboard, name='dashboard'), # 仪表盘
]
path('verify/<uidb64>/<token>/', views.verify_email, name='verify_email'),
=======
    # 核心修改：访问 http://127.0.0.1:8000/ 直接触发登录逻辑
    path('', views.login_view, name='login'),

    # 主页路径：登录成功后跳转到这里
    path('mainpage/', views.mainpage_view, name='mainpage'),
    
    # 身份验证相关
    path('logout/', views.user_logout, name='logout'),
    path('register/', views.register_view, name='register'),
    path('forgot/', views.forgot_view, name='forgot'),
    
    # 其他功能页面
    path('profile/', views.profile_view, name='profile'),
    path('feedback/', views.feedback_view, name='feedback'),
    path('article/', views.article_view, name='article'),
    path('moodentry/', views.moodentry_view, name='moodentry'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('gallery/', views.gallery_view, name='gallery'),
    path('search/', views.search_view, name='search'),
]
>>>>>>> b471e3d (combine frontend html and backend)
